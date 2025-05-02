import os
import re
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Base directory
base_dir = '.'

# Find all r* directories
r_dirs = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith('r')])

# Assign consistent colors
num_colors = len(r_dirs)
colors = cm.get_cmap('Paired', num_colors)  # Or Set1, Dark2, etc.

# First, parse all data and find global max y for syncing axes
amr_data = {}
dedup_data = {}
global_max_y = 0

for idx, r_dir in enumerate(r_dirs):
    color = colors(idx)

    # AMR refine times
    amr_refine_path = os.path.join(base_dir, r_dir, 'amr', 'refine_times.txt')
    if os.path.exists(amr_refine_path):
        amr_timesteps = []
        amr_times = []
        with open(amr_refine_path, 'r') as f:
            for line in f:
                match = re.search(r'Refinement at timestep (\d+) took ([\d\.]+) seconds', line)
                if match:
                    timestep = int(match.group(1))
                    time = float(match.group(2))
                    amr_timesteps.append(timestep)
                    amr_times.append(time)
                    if time > global_max_y:
                        global_max_y = time
        amr_data[r_dir] = (amr_timesteps, amr_times, color)
    else:
        print(f"Skipping {r_dir} (no amr/refine_times.txt)")

    # Dedup times
    dedup_refine_path = os.path.join(base_dir, r_dir, 'dedup', 'dedup_times.txt')
    if os.path.exists(dedup_refine_path):
        dedup_timesteps = []
        dedup_times = []
        with open(dedup_refine_path, 'r') as f:
            for line in f:
                match = re.search(r'Deduplication at current_id (\d+) took ([\d\.]+) seconds', line)
                if match:
                    timestep = int(match.group(1))
                    time = float(match.group(2))
                    dedup_timesteps.append(timestep)
                    dedup_times.append(time)
                    if time > global_max_y:
                        global_max_y = time
        dedup_data[r_dir] = (dedup_timesteps, dedup_times, color)
    else:
        print(f"Skipping {r_dir} (no dedup/dedup_times.txt)")

# ---------------- PRINT maximum times ----------------

print("\n=== Maximum Times per Refinement Level ===\n")
print(f"{'Refinement':<10} {'Max AMR Time (s)':>20} {'Max Dedup Time (s)':>20}")
print("-" * 55)

for r_dir in r_dirs:
    amr_max = max(amr_data[r_dir][1]) if r_dir in amr_data else None
    dedup_max = max(dedup_data[r_dir][1]) if r_dir in dedup_data else None

    amr_str = f"{amr_max:.6f}" if amr_max is not None else "N/A"
    dedup_str = f"{dedup_max:.6f}" if dedup_max is not None else "N/A"

    print(f"{r_dir:<10} {amr_str:>20} {dedup_str:>20}")

print("\n")

# ---------------- AMR Refinement Time Plot ----------------

plt.figure(figsize=(12, 8))

for r_dir, (timesteps, times, color) in amr_data.items():
    plt.plot(
        timesteps,
        times,
        label=f'{r_dir}',
        linestyle='-',
        markersize=6,
        linewidth=2,
        color=color
    )

plt.xlabel('Timestep', fontsize=16)
plt.ylabel('Refine Time (seconds)', fontsize=16)
plt.title('AMR Refinement Time per Timestep', fontsize=18)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=14, title="Refinement Level", title_fontsize=14, frameon=False)
plt.xlim(left=0)
plt.ylim(0, global_max_y * 1.1)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.savefig('amr_refine_times.png')
plt.show()

# ---------------- Deduplication Time Plot ----------------

plt.figure(figsize=(12, 8))

for r_dir, (timesteps, times, color) in dedup_data.items():
    plt.plot(
        timesteps,
        times,
        label=f'{r_dir}',
        linestyle='-',
        markersize=6,
        linewidth=2,
        color=color
    )

plt.xlabel('Timestep', fontsize=16)
plt.ylabel('Deduplication Time (seconds)', fontsize=16)
plt.title('Deduplication Time per Timestep', fontsize=18)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=14, title="Refinement Level", title_fontsize=14, frameon=False)
plt.xlim(left=0)
plt.ylim(0, global_max_y * 1.1)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.savefig('dedup_times.png')
plt.show()
