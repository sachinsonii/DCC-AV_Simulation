import pygame
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt

# Constants
WIDTH, HEIGHT = 1388, 768
FPS = 30  # Reduced frame rate for slower simulation
VEHICLE_COUNT = 40
GRID_SIZE = 40  # Size of each grid cell
PROXIMITY_RADIUS = 30  # Proximity radius for vehicles
# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Road Map Autonomous Vehicle Simulation")
clock = pygame.time.Clock()

class Vehicle:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.velocity = random.uniform(1, 2)  # Slower initial velocity
        self.angle = random.choice([0, 90, 180, 270])  # Only move in four directions
        self.action = "Moving"
        self.previous_velocity = self.velocity
        self.neighbors = []  # For communication with other vehicles
        self.consensus_value = None  # For consensus algorithms
        self.color = (0, 0, 255)

    def move(self):
        if self.angle == 0:  # Moving right
            self.x += self.velocity
        elif self.angle == 90:  # Moving down
            self.y += self.velocity
        elif self.angle == 180:  # Moving left
            self.x -= self.velocity
        elif self.angle == 270:  # Moving up
            self.y -= self.velocity

        # Wrap around the screen
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)
        # Display vehicle ID, velocity, action, and direction
        font = pygame.font.SysFont(None, 20)
        action_text = font.render(f"ID: {self.id}, Vel: {self.velocity:.2f}, Action: {self.action}, Dir: {self.angle}", True, (255, 255, 255))
        screen.blit(action_text, (int(self.x) + 10, int(self.y) - 10))
        
        # Draw proximity circle
        pygame.draw.circle(screen, (255, 0, 0, 50), (int(self.x), int(self.y)), PROXIMITY_RADIUS, 1)

    def log_data(self, data_list):
        data_list.append({'id': self.id, 'x': self.x, 'y': self.y, 'velocity': self.velocity})

    def decision_making(self, other_vehicles):
        
        # Decision-making logic based on proximity to other vehicles
        self.neighbors = [other for other in other_vehicles if other.id != self.id and np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2) < PROXIMITY_RADIUS]
        
        if self.neighbors:
            # Consensus Algorithm (Paxos-like)
            proposed_value = self.velocity
            self.consensus_value = self.paxos_decision(proposed_value)
            self.velocity = self.consensus_value
            
            # Control (MPC)
            self.apply_mpc()
            
            # RL Adaptation (simple)
            self.apply_rl()

            # Set action based on decision-making
            self.action = "Adjusting Velocity"


            self.color = (0, 255, 0)

        else:
            self.action = "Normal"

            self.color = (0, 0, 255)


    def paxos_decision(self, proposed_value):
        # Simplified Paxos decision-making
        responses = [neighbor.velocity for neighbor in self.neighbors]
        if responses:
            return np.mean(responses)  # Averages the velocities of neighbors
        return proposed_value  # No decision, retain proposed value

    def apply_mpc(self):
        # Simplified Model Predictive Control
        # Here, we might want to minimize the velocity deviation
        if self.neighbors:
            avg_velocity = np.mean([neighbor.velocity for neighbor in self.neighbors])
            self.velocity += (avg_velocity - self.velocity) * 0.1  # Adjust towards average

    def apply_rl(self):
        # Simple RL-like behavior: adjust based on feedback
        # This example uses a naive approach to mimic learning
        if self.neighbors:
            if self.velocity < np.mean([neighbor.velocity for neighbor in self.neighbors]):
                self.velocity += 0.1  # Increase velocity
            elif self.velocity > np.mean([neighbor.velocity for neighbor in self.neighbors]):
                self.velocity -= 0.1  # Decrease velocity

class RoadNetwork:
    def __init__(self):
        self.vehicles = [Vehicle(i, random.randint(0, WIDTH), random.randint(0, HEIGHT)) for i in range(VEHICLE_COUNT)]
    
    def update(self):
        for vehicle in self.vehicles:
            vehicle.move()
            vehicle.decision_making(self.vehicles)
    
    def draw(self):
        for vehicle in self.vehicles:
            vehicle.draw()

def plot_velocity_over_time(data_log):
    df = pd.DataFrame(data_log)
    plt.figure(figsize=(10, 5))
    for vehicle_id in df['id'].unique():
        vehicle_data = df[df['id'] == vehicle_id]
        plt.scatter(vehicle_data.index, vehicle_data['velocity'], label=f'Vehicle {vehicle_id}')
    
    plt.title('Vehicle Velocity Over Time')
    plt.xlabel('Time (Frames)')
    plt.ylabel('Velocity')
    plt.legend()
    plt.grid()
    plt.show()

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))

def main():
    running = True
    road_network = RoadNetwork()
    data_log = []
    

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))  # Clear the screen
        draw_grid()  # Draw the grid
        road_network.update()    # Update vehicle positions
        road_network.draw()      # Draw vehicles

        # Log vehicle data
        for vehicle in road_network.vehicles:
            vehicle.log_data(data_log)

        pygame.display.flip()  # Update the display
        clock.tick(FPS)        # Maintain the frame rate

    pygame.quit()


    # Create DataFrame for analysis and plot
    plot_velocity_over_time(data_log)

if __name__ == "__main__":
    main()
