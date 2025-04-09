#!/usr/bin/env python3
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

def parse_checkpoint_file(filename):
    """Read the checkpoint file and return a list of composition strings."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def checkpoint_to_numeric_array(checkpoint, mapping):
    """
    Convert a checkpoint string into a numeric array based on a mapping.
    For example, mapping: {'o':0, 's':0, 'f':0, 'O':1, 'S':2, 'F':3}
    """
    return np.array([mapping[ch] for ch in checkpoint], dtype=np.int32)

def plot_checkpoints_imshow(checkpoints, mapping, save_path):
    # Convert each checkpoint string to a numeric array using only the first 16 characters.
    data = np.array([checkpoint_to_numeric_array(cp, mapping) for cp in checkpoints])
    
    # Transpose the data so that each checkpoint is a column.
    data = data.T  # shape becomes (16, num_checkpoints)
    
    # Define colors corresponding to each numeric value.
    # Index 0 (all lowercase markers) will be lightgray,
    # while uppercase markers get distinct colors.
    colors = ['whitesmoke', 'lightblue', 'orange', 'lightgreen']
    cmap = ListedColormap(colors)
    
    # Create figure: adjust width according to the number of checkpoints, and use a shorter height.
    fig, ax = plt.subplots(figsize=(len(checkpoints)*0.3 + 3, 4))
    
    # Use imshow with nearest interpolation to render each "pixel" as a block.
    im = ax.imshow(data, aspect='auto', cmap=cmap, interpolation='nearest')
    # ax.set_xlabel("Checkpoint")
    ax.set_ylabel("Chunk Index")
    ax.set_title("Checkpoint Composition: 25_25_50")
    
    # Set x-ticks so that each checkpoint is labeled in the center of its column.
    ax.set_xticks(np.arange(len(checkpoints)))
    ax.set_xticklabels([f'Chkpt {i}' for i in range(len(checkpoints))], rotation=90)
    
    # Add vertical lines between columns to clearly separate each checkpoint.
    for i in range(len(checkpoints) - 1):
        ax.axvline(x=i + 0.5, color='white', linewidth=1)
    
    # --- Updated Legend ---
    # Only uppercase letters will appear in the legend.
    legend_order = ['O', 'S', 'F']
    legend_labels = {
        'O': 'first occur',
        'S': 'shifted dupe',
        'F': 'fixed dupe'
    }
    legend_handles = []
    for letter in legend_order:
        idx = mapping[letter]
        legend_handles.append(mpatches.Patch(color=colors[idx], label=legend_labels[letter]))
    ax.legend(handles=legend_handles, title="Chunk Type", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Graph saved to {save_path}")

def main():
    input_file = "/home/zmalk/Research/ANL/checkpoint_restore/gpu-dedup/build/temp/256_floats_test._checkpoint_history.txt"
    output_file = "/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/graphs/chunk_distro_graph.png"
    
    checkpoints = parse_checkpoint_file(input_file)
    # Remap all lowercase letters to 0 (lightgray) and assign distinct values to uppercase.
    mapping = {
        'o': 0,
        's': 0,
        'f': 0,
        'O': 1,
        'S': 2,
        'F': 3
    }
    
    plot_checkpoints_imshow(checkpoints, mapping, save_path=output_file)

if __name__ == '__main__':
    main()
