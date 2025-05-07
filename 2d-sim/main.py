'''
Author: Zack Malkmus
Date: 5/2/2025
This is a simple simulation of a 2D mesh of doubles that gets perturbed by a sphere moving across the plane. 
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

# TODO: Apply boolean map overlay of first occurrences and shifted duplicates are located on the mesh.

from sim import Simulation

def main():
    sim = Simulation(size=4, sim_length=10, perturbation=0.0000001, max_refinement=0, shape_affects_mesh=True, uniform_refinement=False, plot=True)
    # sim = Simulation(seed=42, size=10, sim_length=10, perturbation=0.01, max_refinement=3, uniform_refinement=False, plot=True)

if __name__ == "__main__":
    main()