from block import Block
from sim import Simulation

# ────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ────────────────────────────────────────────────────────────────────────────
def _leaf_blocks(block: Block):
    """Return a flat list of every *leaf* block under—or equal to—`block`."""
    if block.active:
        return [block]
    leaves = []
    for child in block.children:
        leaves.extend(_leaf_blocks(child))
    return leaves


def _leaf_blocks_grid(grid):
    """All leaves in the entire grid."""
    leaves = []
    for row in grid:
        for blk in row:
            leaves.extend(_leaf_blocks(blk))
    return leaves


def _print_leaf_blocks(block: Block, indent: int = 0) -> None:
    """Recursively print leaf extents—for visual inspection only."""
    if block.active:
        print(" " * indent +
              f"[{block.xmin:.2f},{block.xmax:.2f}] × "
              f"[{block.ymin:.2f},{block.ymax:.2f}]  (L{block.level})")
        return
    for child in block.children:
        _print_leaf_blocks(child, indent + 2)


# ────────────────────────────────────────────────────────────────────────────
# Main test routine
# ────────────────────────────────────────────────────────────────────────────
def test_refine_and_coarsen() -> None:
    print("\n=== BUILD 2×2 ROOT GRID ===")
    sim = Simulation(size=2, seed=0, sim_length=0)      # grid only
    roots = [blk for row in sim.grid for blk in row]

    # ── level-0 checks ──────────────────────────────────────────────────
    leaves = _leaf_blocks_grid(sim.grid)
    assert len(leaves) == 4, "Initial leaf count should be 4"
    print("Initial leaf blocks:")
    for row in sim.grid:
        for blk in row:
            _print_leaf_blocks(blk)

    sim.plot_grid()

    # ── refine all 4 roots → level 1 ────────────────────────────────────
    print("\n=== REFINE all root blocks to level-1 ===")
    for r in roots:
        r.refine()

    leaves = _leaf_blocks_grid(sim.grid)
    assert len(leaves) == 16, "After refining 4 roots we expect 16 leaves"
    assert all(leaf.level == 1 for leaf in leaves), "All leaves should be level-1"
    print(f"Leaf count after level-1 refinement: {len(leaves)}")

    sim.plot_grid()

    # ── drill one branch to level-2 ─────────────────────────────────────
    branch_lvl1 = roots[0].children[0]         # pick UL-of-UL leaf
    branch_lvl1.refine()

    leaves = _leaf_blocks_grid(sim.grid)
    assert len(leaves) == 19, "Refining one L1 leaf adds 3 leaves (16-1+4)"
    assert max(l.level for l in leaves) == 2, "Deepest level should now be 2"
    print(f"Leaf count after level-2 refinement: {len(leaves)}")

    sim.plot_grid()

    # ── drill one grand-child to level-3 ───────────────────────────────
    branch_lvl2 = branch_lvl1.children[0]
    branch_lvl2.refine()

    leaves = _leaf_blocks_grid(sim.grid)
    assert len(leaves) == 22, "Refining one L2 leaf adds 3 more leaves"
    assert max(l.level for l in leaves) == 3, "Deepest level should now be 3"
    print(f"Leaf count after level-3 refinement: {len(leaves)}")

    sim.plot_grid()

    # ── coarsen back: level-3 → level-2 ────────────────────────────────
    print("\n=== COARSEN level-3 branch back to level-2 ===")
    branch_lvl2.coarsen()
    leaves = _leaf_blocks_grid(sim.grid)
    assert len(leaves) == 19 and max(l.level for l in leaves) == 2

    sim.plot_grid()

    # ── coarsen level-2 branch back to level-1 ─────────────────────────
    print("=== COARSEN level-2 branch back to level-1 ===")
    branch_lvl1.coarsen()
    leaves = _leaf_blocks_grid(sim.grid)
    assert len(leaves) == 16 and max(l.level for l in leaves) == 1

    sim.plot_grid()

    # ── coarsen every root back to level-0 ─────────────────────────────
    print("=== COARSEN all roots back to level-0 ===")
    for r in roots:
        r.coarsen()
    leaves = _leaf_blocks_grid(sim.grid)
    assert len(leaves) == 4 and max(l.level for l in leaves) == 0
    print("Leaf count after full coarsen:", len(leaves))

    sim.plot_grid()

    print("\n✓ Deep refine/coarsen test passed!")