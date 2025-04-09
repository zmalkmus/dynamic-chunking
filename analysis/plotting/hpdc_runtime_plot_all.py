import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

def get_full_avg(file):
    full_df = pd.read_csv(file, header=None)
    # Assuming the runtime values are in the 5th column (index 4)
    avg_runtime = full_df[4].mean()
    return avg_runtime

def plot(df, full_avg):
    # Ensure numeric types.
    df["i"] = pd.to_numeric(df["i"])
    df["chunk_size"] = pd.to_numeric(df["chunk_size"])
    df["runtime"] = pd.to_numeric(df["runtime"])
    
    # Define chunk_sizes (rows) and dedup_cases (columns) with new order.
    chunk_sizes = [1024, 2048, 4096]
    dedup_cases = ["0_100_0", "25_25_50", "80_10_10", "100_0_0"]
    
    # The method names as present in the dataset.
    method_order = [
        "basic",
        "list",
        "Tree_Baseline",  # This is the actual dataset name.
        "Tree_Posix",
        "Tree_Liburing_Optimized"
    ]
    
    # Use the fixed order for assigning colors and hatch patterns.
    global_colors = sns.color_palette("colorblind", n_colors=len(method_order))
    method_colors = {method: global_colors[i] for i, method in enumerate(method_order)}
    
    hatch_patterns = [r'//', r'\\', r'++', r'XX']
    method_hatches = {method: hatch_patterns[i % len(hatch_patterns)] for i, method in enumerate(method_order)}
    
    # Fixed break threshold for the y-axis.
    y_break = 20
    
    # Create an outer GridSpec with 3 rows x 4 columns.
    fig = plt.figure(figsize=(15, 10))
    outer = gridspec.GridSpec(3, 4, wspace=0.2, hspace=0.1)
    
    # Iterate over chunk_sizes (rows) and dedup_cases (columns).
    for row_idx, cs in enumerate(chunk_sizes):
        df_cs = df[df["chunk_size"] == cs]
        for col_idx, d_case in enumerate(dedup_cases):
            gs_cell = outer[row_idx, col_idx]
            # Create an inner GridSpec for the broken y-axis (2 panels per cell).
            inner = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_cell,
                                                     height_ratios=[1, 2], hspace=0.15)
            ax_upper = plt.Subplot(fig, inner[0])
            ax_lower = plt.Subplot(fig, inner[1])
            fig.add_subplot(ax_upper)
            fig.add_subplot(ax_lower)
            
            # Filter data for this chunk_size and dedup_case.
            df_sub = df_cs[df_cs["dedup_case"] == d_case]
            if not df_sub.empty:
                stats = df_sub.groupby("method")["runtime"].agg(["mean", "std"])
                # Reindex using the desired order and drop methods not present.
                stats = stats.reindex(method_order).dropna()
                for pos, (method, row_stats) in enumerate(stats.iterrows()):
                    ax_upper.bar(pos, row_stats["mean"], yerr=row_stats["std"], capsize=3,
                                 color=method_colors[method], hatch=method_hatches[method], width=1.0)
                    ax_lower.bar(pos, row_stats["mean"], yerr=row_stats["std"], capsize=3,
                                 color=method_colors[method], hatch=method_hatches[method], width=1.0)
                max_val = (stats["mean"] + stats["std"]).max()
            else:
                max_val = y_break
            
            if max_val <= y_break:
                upper_ylim = y_break + 1
            else:
                upper_ylim = max_val * 1.1
            
            # Set y-axis limits for the broken y-axis panels.
            ax_lower.set_ylim(0, y_break)
            ax_upper.set_ylim(y_break, upper_ylim)
            
            # Draw a continuous solid black horizontal line for full_avg.
            if full_avg < y_break:
                ax_lower.axhline(full_avg, color='black', linestyle='-', linewidth=1)
            elif full_avg > y_break:
                ax_upper.axhline(full_avg, color='black', linestyle='-', linewidth=1)
            else:
                ax_lower.axhline(full_avg, color='black', linestyle='-', linewidth=1)
                ax_upper.axhline(full_avg, color='black', linestyle='-', linewidth=1)
            
            # Hide the connecting spines.
            ax_upper.spines['bottom'].set_visible(False)
            ax_lower.spines['top'].set_visible(False)
            ax_upper.tick_params(labelbottom=False)
            
            # Add diagonal break lines.
            d_size = 0.015
            kwargs = dict(transform=ax_upper.transAxes, color='k', clip_on=False)
            ax_upper.plot((-d_size, d_size), (-d_size, d_size), **kwargs)
            ax_upper.plot((1 - d_size, 1 + d_size), (-d_size, d_size), **kwargs)
            kwargs.update(transform=ax_lower.transAxes)
            ax_lower.plot((-d_size, d_size), (1 - d_size, 1 + d_size), **kwargs)
            ax_lower.plot((1 - d_size, 1 + d_size), (1 - d_size, 1 + d_size), **kwargs)
            
            # Remove x-ticks.
            ax_upper.set_xticks([])
            ax_lower.set_xticks([])
            
            # Remove y-ticks from the upper panel if there is no data above the break.
            if max_val <= y_break:
                ax_upper.set_yticks([])
            
            # Maintain individual labels:
            # Label the leftmost column with the chunk_size.
            if col_idx == 0:
                ax_lower.set_ylabel(f"{cs}", fontsize=12, rotation=0, labelpad=40)
            # Label the bottom row with the dedup_case.
            if row_idx == (len(chunk_sizes) - 1):
                if d_case == "0_100_0":
                    ax_lower.set_xlabel("0% First Occurs\n100% Fixed Dupes\n0% Shifted Dupes", fontsize=12, rotation=0, labelpad=8)
                elif d_case == "100_0_0":
                    ax_lower.set_xlabel("100% First Occurs\n0% Fixed Dupes\n0% Shifted Dupes", fontsize=12, rotation=0, labelpad=8)
                elif d_case == "25_25_50":
                    ax_lower.set_xlabel("25% First Occurs\n25% Fixed Dupes\n50% Shifted Dupes", fontsize=12, rotation=0, labelpad=8)
                elif d_case == "80_10_10":
                    ax_lower.set_xlabel("80% First Occurs\n10% Fixed Dupes\n10% Shifted Dupes", fontsize=12, rotation=0, labelpad=8)

    # Build a custom legend.
    legend_order = [
        "basic",
        "list",
        "Tree_Baseline",  # Remains as in dataset.
        "Tree_Posix",
        "Tree_Liburing_Optimized"
    ]
    
    # Alias "Tree_Baseline" to "Tree_Naive" in the legend.
    rename_map = {"basic": "Basic", "list": "List", "Tree_Baseline": "Tree_Naive"}
    legend_handles = [
        mpatches.Patch(
            facecolor=method_colors[method],
            hatch=method_hatches[method],
            label=rename_map.get(method, method)
        )
        for method in legend_order
    ]
    
    # Create the "Full" line legend entry and prepend it.
    full_handle = Line2D([0], [0], color='black', lw=2, label='Full')
    legend_handles = [full_handle] + legend_handles
    
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.95),
        title="Method",
        ncol=len(legend_handles)
    )
    
    fig.suptitle("Average Checkpoint Restore Time Per Chunk Distribution and Chunk Size", fontsize=20)
    fig.text(0.5, 0.01, "Chunk Distribution", ha="center", fontsize=16)
    fig.text(0.04, 0.5, "Chunk Size", va="center", rotation="vertical", fontsize=16)
    
    # Save the plot
    plt.savefig("/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/graphs/graph1.png", bbox_inches="tight")
    plt.show()

def main():
    results_path = "/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/data/HPDC25/"
    combined_file = results_path + "combined_results.csv"
    full_avg = get_full_avg(results_path + "full_restore.csv")
    df = pd.read_csv(combined_file, header=0)
    plot(df, full_avg)

if __name__ == "__main__":
    main()
