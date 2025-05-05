'''
Author: Zack Malkmus
Date: 5/2/2025
This is a simple simulation of a 2D grid of doubles that gets perturbed by a sphere moving across the plane. 
This is a test for deduplication of miniAMR.

+---+---+---+---+---+
| O |   |   |   |   |
+---+---+---+---+---+
| O | O |   |   |   |
+---+---+---+---+---+
| O |   |   |   |   |
+---+---+---+---+---+

+---+---+---+---+---+
|   | O |   |   |   |
+---+---+---+---+---+
| O | O | O |   |   |
+---+---+---+---+---+
|   | O |   |   |   |
+---+---+---+---+---+

+---+---+---+---+---+
|   |   | O |   |   |
+---+---+---+---+---+
|   | O | O | O |   |
+---+---+---+---+---+
|   |   | O |   |   |
+---+---+---+---+---+

+---+---+---+---+---+
|   |   |   | O |   |
+---+---+---+---+---+
|   |   | O | O | O |
+---+---+---+---+---+
|   |   |   | O |   |
+---+---+---+---+---+

+---+---+---+---+---+
|   |   |   |   | O |
+---+---+---+---+---+
|   |   |   | O | O |
+---+---+---+---+---+
|   |   |   |   | O |
+---+---+---+---+---+

'''

from sim import Simulation
from block import Block

def main():
    sim = Simulation(size=10, sim_length=3, perturbation=0.1, max_refinement=3)

if __name__ == "__main__":
    main()