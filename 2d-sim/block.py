import random
import numpy as np

class Block:
    """
    A 2D block of data.

    Hold 4 values, x1,x2,x3,x4, which are the corners of the block.
    The block is represented as a 2D numpy array of shape (2,2).
    The block is initialized with random values between 0 and 1.
    [b0|b1]
    [b2|b3]
    """

    def __init__(self, sim, xmin, xmax, ymin, ymax, level=0):
        self.active = True
        self.sim    = sim
        self.xmin   = xmin
        self.xmax   = xmax
        self.ymin   = ymin
        self.ymax   = ymax

        self.x1 = self.sim.rng.uniform(0, 1)
        self.x2 = self.sim.rng.uniform(0, 1)
        self.x3 = self.sim.rng.uniform(0, 1)
        self.x4 = self.sim.rng.uniform(0, 1)

        self.children = []
        self.level = level
        self.parent = None

        return
    
    def center(self):
        x = (self.xmin + self.xmax) / 2
        y = (self.ymin + self.ymax) / 2
        return x, y
    
    def get_root(self):
        """
        Get the root block of the tree.
        """

        if self.parent is None:
            return self
        else:
            return self.parent.get_root()
    
    # =========================================================
    # Simulation Logic
    # =========================================================
    
    def perturb(self, perturbation):
        """
        Perturb the block by a random value between -perturbation and perturbation.
        """

        if not self.active:
            for child in self.children:
                child.perturb(perturbation)
            return
        else:
            new_x1 = self.x1 + self.sim.rng.uniform(-perturbation, perturbation)
            new_x2 = self.x2 + self.sim.rng.uniform(-perturbation, perturbation)
            new_x3 = self.x3 + self.sim.rng.uniform(-perturbation, perturbation)
            new_x4 = self.x4 + self.sim.rng.uniform(-perturbation, perturbation)

            self.x1 = max(0.0, new_x1)
            self.x2 = max(0.0, new_x2)
            self.x3 = max(0.0, new_x3)
            self.x4 = max(0.0, new_x4)
        return
    
    def refine(self):
        """
        Refine the block by creating 4 children blocks.
        """

        if not self.active:
            return

        cx, cy = self.center()
        self.children = [
            Block(self.sim, self.xmin, cx, self.ymin, cy), #b0
            Block(self.sim, cx, self.xmax, self.ymin, cy), #b1
            Block(self.sim, self.xmin, cx, cy, self.ymax), #b2
            Block(self.sim, cx, self.xmax, cy, self.ymax)  #b3
        ]

        # Set the level of the children blocks
        for i in range(4):
            # Set parent
            self.children[i].level = self.level + 1
            self.children[i].parent = self

            # Set the values of the children blocks based on the parent block
            self.children[i].x1 = self.sim.rng.uniform(self.x2, self.x3)
            self.children[i].x2 = self.sim.rng.uniform(self.x1, self.x4)
            self.children[i].x3 = self.sim.rng.uniform(self.x1, self.x4)
            self.children[i].x4 = self.sim.rng.uniform(self.x2, self.x3)

        # Update the simulation's leaf cache
        self.sim.leaves.remove(self)
        self.sim.leaves.extend(self.children)

        self.active = False
        return
    
    def coarsen(self):
         # 1. Leaf blocks have nothing to collapse.
        if self.active:
            return

        # 2. Defensive-guard: no children?  Just mark the block active again.
        if not self.children:
            self.active = True
            return

        # 3. Recursively coarsen every child first.
        for child in self.children:
            child.coarsen()

        # 4. Aggregate corner values from the (now-leaf) children.
        n = len(self.children) # typically 4, but stay generic
        self.x1 = sum(c.x1 for c in self.children) / n
        self.x2 = sum(c.x2 for c in self.children) / n
        self.x3 = sum(c.x3 for c in self.children) / n
        self.x4 = sum(c.x4 for c in self.children) / n

        # 5. Release fine blocks and reactivate this one.
        self.sim.leaves.remove(self.children[0])
        self.sim.leaves.remove(self.children[1])
        self.sim.leaves.remove(self.children[2])
        self.sim.leaves.remove(self.children[3])
        self.sim.leaves.append(self)

        self.children.clear()
        self.active = True
        return
    
    # =========================================================
    # I/O
    # =========================================================
    
    def binary_dump(self, filename, dtype=np.float32):
        arr = np.asarray([self.x1, self.x2, self.x3, self.x4], dtype=dtype)
        arr.tofile(open(filename, "ab"))
        return
