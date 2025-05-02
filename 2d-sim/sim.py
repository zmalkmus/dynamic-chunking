import random
import numpy as np

class Simulation:
    def __init__(self, size, seed=None, sim_length=10, perturbation=0.1):
        self.rng            = random.Random(seed)
        self.sim_length     = sim_length
        self.perturbation   = perturbation
        self.timestep       = 0
        self.size           = size
        self.grid           = self.__initialize_grid(size)
        
        self.run()
        return

    def __initialize_grid(self, size):
        grid = [0 for _ in range(size)]

        for row in range(size):
            grid[row] = [random.uniform(0, 1) for _ in range(size)]

        return grid
    
    def __print_grid(self):
        print(f"Time step: {self.timestep}")
        print("=====================================================================================================")
        for row in self.grid:
            print(row)
        print("=====================================================================================================")
        print()
        return
    
    def __perturb_grid(self):
        for row in range(self.size):
            for col in range(self.size):
                self.grid[row][col] += random.uniform(-1, 1) * self.perturbation
                if self.grid[row][col] < 0:
                    self.grid[row][col] = -self.grid[row][col]
                elif self.grid[row][col] > 1:
                    self.grid[row][col] = 2 - self.grid[row][col]
        return
    
    def __apply_sphere(self):


        return
    
    def run(self):
        while self.timestep < self.sim_length:
            self.__perturb_grid()
            self.__apply_sphere()
            self.timestep += 1
            self.__print_grid()
        return