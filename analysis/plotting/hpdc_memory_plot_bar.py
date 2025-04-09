import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from matplotlib.lines import Line2D  # Needed for the full method legend handle
import matplotlib.ticker as mticker

def compute_mem_hw_stats(file_list):
    """
    For a list of memspace_usage files, compute the maximum
    "HighWater-Process(MB)" from each file and return the mean and std.
    """
    values = []
    for fpath in file_list:
        df = pd.read_csv(
            fpath,
            comment="#",
            header=None,
            delim_whitespace=True,
            names=["Time(s)", "Size(MB)", "HighWater(MB)", "HighWater-Process(MB)"]
        )
        max_val = df["HighWater-Process(MB)"].max()
        values.append(max_val)
    if values:
        return np.mean(values), np.std(values)
    else:
        return np.nan, np.nan

def main():
    # sns.set_style("whitegrid")
    sns.set_context("paper")


    # Base directory where memory usage results are stored
    root_dir = "/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/data/HPDC25/mem_results"
    chunk_size = "2048"

    # Define all available methods (folder names in the data directory).
    # Note: "full" will be drawn as a horizontal line.
    all_methods = ["basic", "full", "list", "tree_naive", "tree_posix", "tree_liburing_optimized"]
    bar_methods = ["basic", "list", "tree_naive", "tree_posix", "tree_liburing_optimized"]

    # Updated display labels for consistency with runtime graph.
    label_map = {
        "basic": "Basic",
        "list": "List",
        "tree_naive": "Tree_Naive",
        "tree_posix": "Tree_Posix",
        "tree_liburing_optimized": "Tree_Liburing_Optimized",
        "full": "Full"
    }

    # **New Order for Test Cases**:
    cases = ["0_100_0", "25_25_50", "80_10_10", "100_0_0"]
    dedup_labels = {
        "0_100_0": "0% First Occurs\n100% Fixed Dupes\n0% Shifted Dupes",
        "100_0_0": "100% First Occurs\n0% Fixed Dupes\n0% Shifted Dupes",
        "25_25_50": "25% First Occurs\n25% Fixed Dupes\n50% Shifted Dupes",
        "80_10_10": "80% First Occurs\n10% Fixed Dupes\n10% Shifted Dupes",
    }

    # Compute memory highwater stats for each test case and method.
    data = {case: {} for case in cases}
    for case in cases:
        for method in all_methods:
            case_path = os.path.join(root_dir, chunk_size, method, case)
            file_list = [
                os.path.join(case_path, f)
                for f in os.listdir(case_path)
                if f.endswith("-Host.memspace_usage")
            ]
            file_list.sort()
            mean_val, std_val = compute_mem_hw_stats(file_list)
            data[case][method] = (mean_val, std_val)

    # Assign colors and hatch patterns to match runtime graph styling.
    # Use only the bar_methods (exclude "full" since it's drawn as a line)
    method_order = bar_methods
    global_colors = sns.color_palette("colorblind", n_colors=len(method_order))
    method_colors = {method: global_colors[i] for i, method in enumerate(method_order)}

    hatch_patterns = [r'//', r'\\', r'++', r'XX']
    method_hatches = {method: hatch_patterns[i % len(hatch_patterns)] for i, method in enumerate(method_order)}

    # Create a figure with 1 row x 4 columns, sharing the y-axis.
    fig, axes = plt.subplots(nrows=1, ncols=len(cases), sharey=True, figsize=(15, 8))
    
    # Loop through each test case and plot bars.
    for ax, case in zip(axes, cases):
        stats = {method: {"mean": data[case][method][0], "std": data[case][method][1]} for method in all_methods}

        # Plot bars in the desired order.
        for pos, method in enumerate(bar_methods):
            m_mean = stats[method]["mean"]
            m_std = stats[method]["std"]
            if not np.isnan(m_mean):
                ax.bar(
                    pos, m_mean, yerr=m_std, capsize=3, width=1,
                    color=method_colors[method], hatch=method_hatches[method],
                )

        # Draw a horizontal line for the "full" method.
        full_mean = stats["full"]["mean"]
        if not np.isnan(full_mean):
            ax.axhline(full_mean, color='black', linestyle='-', linewidth=1)

        # Remove numeric x tick labels.
        ax.set_xticks([])
        # Set descriptive test case labels.
        ax.set_xlabel(dedup_labels[case], fontsize=12)
        # Adjust y tick parameters to bring labels closer to the graph.
        ax.tick_params(axis='y', labelsize=12, pad=2, labelleft=True)
        
        # Make the plot border (axes spines) thicker and black.
        for spine in ax.spines.values():
            spine.set_linewidth(0.8)
            spine.set_color("black")

    # Set shared y-axis label.
    fig.text(0.08, 0.5, "Avg Memory HighWater (MB) Over 10 Iterations", va='center', rotation='vertical', fontsize=14)

    # Title consistency.
    fig.suptitle("Memory HighWater Usage (1GB × 16 Files, 2048 B Chunks)", fontsize=20)

    full_handle = Line2D([0], [0], color='black', lw=2, label=label_map["full"])
    legend_handles = [full_handle] + [
        mpatches.Patch(
            facecolor=method_colors[method],
            hatch=method_hatches[method],
            edgecolor='black',
            label=label_map[method]
        )
        for method in bar_methods
    ]

    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.95),
        title="Method",
        ncol=len(legend_handles)
    )

    # Adjust the layout to give room for the title and legend.
    plt.tight_layout(rect=[0.1, 0, 1, 0.95])

    # Save and display the figure.
    save_path = "/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/graphs/HPDC25/hpdc25_mem_bar.png"
    plt.savefig(save_path, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    main()
