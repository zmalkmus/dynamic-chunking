import random
from block import Block
from shape import Circle
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import os

class Simulation:
    """
    A 2D simulation of a mesh of blocks.

    The simulation is initialized with a mesh of blocks.
    Each block is a collection of 4 values, 1 for each corner of the block.
    [x1|x2]
    [x3|x4]
    The blocks are initialized with random values between 0 and 1.
    The blocks are perturbed by a random value between -perturbation and perturbation.
    The blocks are refined by splitting the blocks in half in each direction, creating 4 children blocks.
    The blocks are refined by a given number of levels.
    """

    def __init__(self, size, seed=None, sim_length=10, perturbation=0.1, max_refinement=3, shape_affects_mesh = True, uniform_refinement=False, plot=False, output_dir="data"):
        if seed is None:
            seed = random.randint(0, 100000)

        self.seed                = seed
        self.rng                 = random.Random(seed)
        self.sim_length          = sim_length
        self.perturbation        = perturbation
        self.max_refinement      = max_refinement
        self.uniform_refinement  = uniform_refinement
        self.shape_affects_mesh  = shape_affects_mesh
        self.size                = size
        self.timestep            = 0
        self.mesh: list[Block]   = []
        self.leaves: list[Block] = []
        self.shape_list          = []
        self.output_dir          = output_dir + "/" + str(seed) + "/"
        self.plot                = plot

        # Print simulation parameters
        print("==========================================================")
        print(f"Running simulation with seed {self.seed} and length {self.sim_length}")
        print(f"Perturbation: {self.perturbation}")
        print(f"Max refinement: {self.max_refinement}")
        print(f"Uniform refinement: {self.uniform_refinement}")
        print(f"Output directory: {self.output_dir}")
        print("==========================================================")

        # Create shapes first so they are consistent across runs
        p = self.__generate_shape_path(sim_length)
        self.plot_path(p)
        self.shape_list.append(Circle(p, 0.25))

        # Initialize the mesh
        if not self.uniform_refinement:
            self.__initialize_mesh()
        else:
            self.__initialize_uniform_mesh()
        self.__initialize_leaves()

        # Plot the initial mesh
        if self.plot:
            self.plot_mesh()

        # Run the simulation
        self.run()
        return

    def __initialize_mesh(self):
        N = self.size
        step_size = 1.0 / N
        self.mesh = [[None for _ in range(N)] for _ in range(N)]
        
        for r in range(N):
            for c in range(N):
                x_min = c * step_size
                x_max = (c + 1) * step_size
                y_min = r * step_size
                y_max = (r + 1) * step_size

                # Create a block with random values
                self.mesh[r][c] = Block(self, x_min, x_max, y_min, y_max)
        return
    
    def __initialize_uniform_mesh(self):
        Nu = self.size * (2 ** self.max_refinement)
        step_size = 1.0 / Nu
        self.mesh = [[None for _ in range(Nu)] for _ in range(Nu)]

        for r in range(Nu):
            for c in range(Nu):
                x_min = c * step_size
                x_max = (c + 1) * step_size
                y_min = r * step_size
                y_max = (r + 1) * step_size

                self.mesh[r][c] = Block(self, x_min, x_max, y_min, y_max)
    
    def __initialize_leaves(self):
        """
        Initialize a cache of all active blocks in the mesh
        """
        if len(self.mesh) == 0:
            raise ValueError("Grid is empty. Cannot initialize leaves.")

        for row in self.mesh:
            for block in row:
                if block.active:
                    self.leaves.append(block)
        return
    
    # =========================================================
    # Simulation Logic
    # =========================================================

    def run(self):
        while self.timestep < self.sim_length:
            self.__step()
            self.dump_simulation()
            self.plot_mesh()
        return
    
    def __step(self):
        self.__perturb_mesh()
        self.__apply_shape(self.shape_list[0])
        if not self.uniform_refinement:
            self.__enforce_refinement()
        
        self.timestep += 1
        return

    def __perturb_mesh(self):
        for block in self.leaves:
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

            # refine only if we need more resolution and*we are still below the refinement cap
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
    
    def __enforce_refinement(self):
        for _ in range(self.max_refinement):

            for leaf in self.leaves:
                neighbors = self.__get_block_neighbors(leaf)
                for n in neighbors:
                    if n.level < leaf.level - 1:
                        n.refine()
        return
    
    def  __get_block_neighbors(self, block):
        """
        Get the neighbors of a block in the mesh.
        """
        neighbors = []
        for blk in self.leaves:
            if blk != block and blk.active:
                if (blk.xmin <= block.xmax and blk.xmax >= block.xmin and
                    blk.ymin <= block.ymax and blk.ymax >= block.ymin):
                    neighbors.append(blk)
        return neighbors
        
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

        y_start = self.rng.random()
        y_end   = self.rng.random()

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
        1. Recursively traverse the mesh and check if the shape intersects with the block.
        2. If the block is active and intersects with the shape, refine the block.
        3. If the block is not active, check if any of its children are active and intersect with the shape.
        4. If any of the children are active and intersect with the shape, refine the block.
        5. If the block is not active and none of its children are active, do nothing.
        """
        
        print("TS: " + str(self.timestep) + " Center at " + str(shape.center(self.timestep)))

        if not self.uniform_refinement:
            for row in self.mesh:
                for block in row:
                    _ = self.__do_refinement(block, shape)
        if self.shape_affects_mesh:
            self.__perturb_mesh_by_shape(shape)
        return
    
    def __perturb_mesh_by_shape(self, shape):
        """
        Perturb only those leaf blocks whose border the shape crosses
        at the current time‐step.
        """
        for block in self.leaves:
            if shape.border_crosses(self.timestep, block):
                block.perturb(1.0)
        return

    # =========================================================
    # Plotting Logic
    # =========================================================

    def dump_simulation(self):
        """
        Dump the simulation to a file.
        """
        
        filename = f"step_{self.timestep:04d}.dat"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        filename = os.path.join(self.output_dir, filename)
        print(f"Dumping simulation to {filename}")

        for block in self.leaves:
            block.binary_dump(filename)

        return

    def plot_mesh(self, show_internal=False):
        """
        Draw the current AMR layout, coloring each leaf by its mean value.
        """
        if not self.plot:
            return

        # choose a colormap and a normalizer for values in [0,1]
        cmap = cm.get_cmap("viridis")
        norm = colors.Normalize(vmin=0.0, vmax=1.0)

        fig, ax = plt.subplots(figsize=(12, 12))

        # draw each leaf block
        for leaf in self.leaves:
            # compute the block’s “value” as the average of its four corners
            mean_val = (leaf.x1 + leaf.x2 + leaf.x3 + leaf.x4) / 4.0
            facecol = cmap(norm(mean_val))

            ax.add_patch(
                plt.Rectangle(
                    (leaf.xmin, leaf.ymin),
                    leaf.xmax - leaf.xmin,
                    leaf.ymax - leaf.ymin,
                    edgecolor="black",
                    facecolor=facecol,
                    linewidth=0.5,
                )
            )

        # set up axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal", adjustable="box")
        ax.invert_yaxis()

        # tidy up spines & labels
        ax.spines["left"].set_position(("data", 0))
        ax.spines["right"].set_color("none")
        ax.spines["bottom"].set_color("none")
        ax.spines["top"].set_position(("outward", 0))
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(f"Grid Blocks (TS={self.timestep}, colored by mean value)")

        # add a colorbar
        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])  # only needed for older matplotlib
        cbar = fig.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("mean(block value)")

        # save the figure
        image_dir = os.path.join(self.output_dir, "images")
        os.makedirs(image_dir, exist_ok=True)
        filename = os.path.join(image_dir, f"mesh_{self.timestep:04d}.png")
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close(fig)

    def plot_path(self, path):
        if self.plot:
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

            # move X-axis to the top for a more “mesh-like” feel (optional)
            ax.xaxis.set_ticks_position("top")
            ax.xaxis.set_label_position("top")

            ax.set_title("Path Plot")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.grid(True)

            # save the figure
            image_dir = os.path.join(self.output_dir, "images")
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            filename = os.path.join(image_dir, f"path.png")
            plt.savefig(filename, dpi=300, bbox_inches="tight")
