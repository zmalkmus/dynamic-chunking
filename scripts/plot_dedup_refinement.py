import os
import matplotlib.pyplot as plt

# Base directory (where r2, r3, r4, r5... are located)
base_dir = '.'

# Find all r* directories
r_dirs = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith('r')])

plt.figure(figsize=(10, 6))

for r_dir in r_dirs:
    usage_path = os.path.join(base_dir, r_dir, 'dedup', 'usage.txt')

    if not os.path.exists(usage_path):
        print(f"Skipping {r_dir} (no dedup/usage.txt found)")
        continue

    timesteps = []
    sizes = []

    with open(usage_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split()
        if len(parts) < 9:
            continue  # Skip lines like "total 44332"
        size = int(parts[4])  # size in bytes
        filename = parts[8]

        if filename.startswith("dump_ts") and "_pe" in filename:
            timestep_part = filename.split("_pe")[0]  # e.g., "dump_ts0000"
            timestep = int(timestep_part.replace("dump_ts", ""))
            timesteps.append(timestep)
            sizes.append(size)

    if not timesteps:
        print(f"No data found in {usage_path}")
        continue

    # Sort by timestep
    sorted_pairs = sorted(zip(timesteps, sizes))
    timesteps_sorted, sizes_sorted = zip(*sorted_pairs)

    # Convert sizes to MB
    sizes_MB = [s / (1024**2) for s in sizes_sorted]

    # Plot each refinement level as a separate line
    plt.plot(timesteps_sorted, sizes_MB, label=f'{r_dir}')

# After all refinement levels are plotted:
plt.xlabel('Timestep')
plt.ylabel('Usage (MB)')
plt.title('Disk Usage per Timestep (Deduplication)')
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.grid(True)
plt.legend(title="Refinement Level", fontsize=14)
plt.tight_layout()

# Save the single combined plot
plt.savefig('all_refinement_dedup_usage.png')
plt.show()
