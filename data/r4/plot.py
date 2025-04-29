import os
import matplotlib.pyplot as plt

# Define the methods and their usage.txt paths
methods = {
    'dedup': 'dedup/usage.txt',
    'baseline': 'baseline/usage.txt',
    'amr': 'amr/usage.txt'
}

# Define placeholder names
placeholders = {
    'dedup': 'Deduplication',
    'baseline': 'Full Checkpoint',
    'amr': 'AMR'
}

# Desired plotting order (based on placeholder order you want)
# "baseline" -> "dedup" -> "amr" so Method 2 is on top
plot_order = ['baseline', 'dedup', 'amr']

usage_data = {}

# Parse each usage.txt
for method, path in methods.items():
    timesteps = []
    sizes = []
    total_usage = 0

    with open(path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split()
        if len(parts) < 9:
            continue  # Skip lines like "total 94644"
        size = int(parts[4])
        filename = parts[8]

        if filename.startswith("dump_ts") and "_pe" in filename:
            timestep_part = filename.split("_pe")[0]  # "dump_ts0000"
            timestep = int(timestep_part.replace("dump_ts", ""))
            timesteps.append(timestep)
            sizes.append(size)
            total_usage += size

    usage_data[method] = {
        'timesteps': timesteps,
        'sizes': sizes,
        'total': total_usage
    }

    print(f"Total usage for {method}: {total_usage / (1024**2):.2f} MB")

# Plot
plt.figure(figsize=(10, 6))
for method in plot_order:  # <- Plot in specified order
    data = usage_data[method]
    sorted_pairs = sorted(zip(data['timesteps'], data['sizes']))
    timesteps_sorted, sizes_sorted = zip(*sorted_pairs)

    sizes_MB = [s / (1024**2) for s in sizes_sorted]
    plt.plot(timesteps_sorted, sizes_MB, label=placeholders[method])  # placeholder label

plt.xlim(left=0)
plt.ylim(bottom=0)
plt.xlabel('Timestep')
plt.ylabel('Usage (MB)')
plt.title('Disk Usage per Timestep (Refinement 4)')
plt.legend(fontsize=20)
plt.grid(True)
plt.tight_layout()
plt.savefig('usage_plot.png')
plt.show()
