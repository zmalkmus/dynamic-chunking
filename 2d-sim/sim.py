import random
from block import Block
from shape import Circle
import matplotlib.pyplot as plt

# TODO: Implement communication between root blocks (2 to 1 rule where no blocks are more than 1 level apart)

class Simulation:
    """
    A 2D simulation of a grid of blocks.

    The simulation is initialized with a grid of blocks.
    Each block is a collection of 4 values, 1 for each corner of the block.
    [x1|x2]
    [x3|x4]
    The blocks are initialized with random values between 0 and 1.
    The blocks are perturbed by a random value between -perturbation and perturbation.
    The blocks are refined by splitting the blocks in half in each direction, creating 4 children blocks.
    The blocks are refined by a given number of levels.
    """

    def __init__(self, size, seed=None, sim_length=10, perturbation=0.1, max_refinement=3):
        self.master_rng     = random.Random(seed)
        self.sim_length     = sim_length
        self.perturbation   = perturbation
        self.timestep       = 0
        self.size           = size
        self.grid           = self.__initialize_grid(size)
        self.max_refinement = max_refinement
        self.shape_list     = []

        p = self.__generate_shape_path(sim_length)
        self.plot_path(p)
        self.shape_list.append(Circle(p, 0.25))

        self.run()
        return

    def __initialize_grid(self, N):
        step_size = 1 / N
        grid = [[None for _ in range(N)] for _ in range(N)]
        
        for r in range(N):
            for c in range(N):
                x_min = c * step_size
                x_max = (c + 1) * step_size
                y_min = r * step_size
                y_max = (r + 1) * step_size

                # Create a block with random values
                grid[r][c] = Block(self.master_rng.randint(0, 100000), x_min, x_max, y_min, y_max)
        return grid
    
    # =========================================================
    # Simulation Logic
    # =========================================================

    def run(self):
        while self.timestep < self.sim_length:
            self.__step()
            self.plot_grid(show_internal=True)
        return
    
    def __step(self):
        self.__perturb_grid()
        self.__apply_shape(self.shape_list[0])
        self.timestep += 1
        return

    def __perturb_grid(self):
        for row in self.grid:
            for block in row:
                block.perturb(self.perturbation)
        return

    def __do_refinement(self, block, shape) -> bool:
        """
        Depth-first refinement / coarsening.

        Returns
        -------
        bool
            True  – this block (or one of its descendants) intersects the
                    shape’s border → keep it (and its parents) refined.
            False – no intersection anywhere below → the whole subtree can be
                    collapsed into this block.
        """
        # leaf block
        if block.active:
            intersects = shape.border_crosses(self.timestep, block)

            # refine only if we *need* more resolution *and* we are still below
            # the refinement cap
            if intersects and block.level < self.max_refinement:
                block.refine()

                # fall through: handle the children right away
                x = False
                for child in block.children:
                    x = self.__do_refinement(child, shape) or x
                return x
            
            # leaf stays as-is
            return intersects

        # internal node
        # recurse on the existing children
        child_hits = [self.__do_refinement(child, shape) for child in block.children]
        any_hit   = any(child_hits)

        all_leaf_children = all(child.active for child in block.children)
        if not any_hit and all_leaf_children:
            block.coarsen()
            return False

        return any_hit

    
    # =========================================================
    # Shape Logic
    # =========================================================
    
    def __generate_shape_path(self, N: int):
        """
        Left-to-right sweep with a changing height.

        • First point  : (0,  y_start)      on the left boundary
        • Last  point  : (1,  y_end)        on the right boundary
        • y_start and y_end are random in [0, 1] (may be equal by chance)
        • Returns N evenly spaced points, including both endpoints.
        """
        assert N >= 2, "need at least two steps to define a path"

        y_start = self.master_rng.random()
        y_end   = self.master_rng.random()

        path = [
            (
                i / (N - 1),                              # x goes 0 → 1
                y_start + (y_end - y_start) * i / (N - 1) # y interpolates
            )
            for i in range(N)
        ]
        return path

    def __apply_shape(self, shape):
        """
        1. Recursively traverse the grid and check if the shape intersects with the block.
        2. If the block is active and intersects with the shape, refine the block.
        3. If the block is not active, check if any of its children are active and intersect with the shape.
        4. If any of the children are active and intersect with the shape, refine the block.
        5. If the block is not active and none of its children are active, do nothing.
        """
        
        print("TS: " + str(self.timestep) + " Center at " + str(shape.center(self.timestep)))

        for row in self.grid:
            for block in row:
                _ = self.__do_refinement(block, shape)
                    
        return

    # =========================================================
    # Plotting Logic
    # =========================================================

    def __flatten_block_list(self):
        """
        Return a flat list of *leaf* blocks ― i.e. every block that is currently
        active (no children).  Internal / inactive blocks are skipped.
        """
        leaves = []

        def dfs(blk):
            if blk.active:
                leaves.append(blk)
            else:
                for child in blk.children:
                    dfs(child)

        for row in self.grid:
            for blk in row:
                dfs(blk)

        return leaves
    

    def plot_grid(self, show_internal=False):
        """
        Draw the current AMR layout.
            • Every active (leaf) block is outlined in black.
            • Optionally, internal blocks can be shown as thin grey dashed boxes.
        The origin (0,0) is placed at the upper-left of the figure.
        """
        ax = plt.figure(figsize=(12, 12)).gca()

        for leaf in self.__flatten_block_list():
            ax.add_patch(
                plt.Rectangle(
                    (leaf.xmin, leaf.ymin),
                    leaf.xmax - leaf.xmin,
                    leaf.ymax - leaf.ymin,
                    edgecolor="black",
                    facecolor="none",
                    linewidth=1.0,
                )
            )

        if show_internal:
            for row in self.grid:
                for blk in row:
                    if not blk.active:
                        ax.add_patch(
                            plt.Rectangle(
                                (blk.xmin, blk.ymin),
                                blk.xmax - blk.xmin,
                                blk.ymax - blk.ymin,
                                edgecolor="grey",
                                facecolor="none",
                                linewidth=0.5,
                                linestyle="--",
                            )
                        )

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal", adjustable="box")
        ax.invert_yaxis()

        ax.spines["left"].set_position(("data", 0))
        ax.spines["right"].set_color("none")
        ax.spines["bottom"].set_color("none")
        ax.spines["top"].set_position(("outward", 0))
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")

        for label in ax.get_xticklabels():
            label.set_rotation(90)
            label.set_verticalalignment("bottom")

        ax.grid(False)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("Grid Blocks (origin at upper-left)")
        plt.show()

    def plot_path(self, path):
        x_vals, y_vals = zip(*path)

        print(f"Path: {path}")

        plt.figure(figsize=(6, 6))
        ax = plt.gca()                       # grab the current Axes
        ax.plot(x_vals, y_vals,
                marker='o', linestyle='-', color='blue')

        # domain and orientation
        ax.set_xlim(0.0, 1.0)               # X: 0 → 1 (left → right)
        ax.set_ylim(0.0, 1.0)               # Y: 0 → 1 (will invert next)
        ax.invert_yaxis()                   # put 0 at the *top*
        ax.set_aspect("equal", adjustable="box")

        # move X-axis to the top for a more “grid-like” feel (optional)
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")

        ax.set_title("Path Plot")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid(True)
        plt.show()
