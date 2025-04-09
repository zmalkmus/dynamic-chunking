import os
import pandas as pd
import matplotlib.pyplot as plt

def read_and_average(file_list, x_col="Time(s)"):
    """
    Given a list of memspace_usage files for a single case,
    read each file, extract the specified x-axis column (default "Time(s)")
    and the "HighWater-Process(MB)" column, then compute the row-wise average
    of both columns.
    
    Returns a DataFrame with columns [x_col, "avg_HW"].
    Assumes all files for a given case have the same number of rows.
    """
    usage_columns = ["Time(s)", "Size(MB)", "HighWater(MB)", "HighWater-Process(MB)"]
    
    time_list = []
    hw_list = []
    
    # Read each file into a separate DataFrame and store the columns of interest
    for idx, fpath in enumerate(file_list):
        df = pd.read_csv(
            fpath,
            comment="#",            # Skip comment lines starting with '#'
            header=None,
            delim_whitespace=True,  # Data is whitespace-delimited
            names=usage_columns
        )
        
        time_list.append(df[x_col].rename(f"time_{idx}"))
        hw_list.append(df["HighWater-Process(MB)"].rename(f"iter_{idx}"))
    
    # Average the x-axis values and the HighWater-Process(MB) values row-wise
    merged_time = pd.concat(time_list, axis=1)
    merged_hw = pd.concat(hw_list, axis=1)
    
    avg_time = merged_time.mean(axis=1)
    avg_hw = merged_hw.mean(axis=1)
    
    # Construct the final DataFrame using the averaged values
    result_df = pd.DataFrame({
        x_col: avg_time,
        "avg_HW": avg_hw
    })
    return result_df

def main():
    root_dir = "/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/data/HPDC25/mem_results"
    # Reorder methods so that the optimized version appears on the right.
    methods = ["full", "basic", "list", "tree_naive", "tree_posix", "tree_liburing_optimized"]
    cases = ["0_100_0", "25_25_50", "80_10_10", "100_0_0"]
    chunk_size = "2048"

    # Predefine colors so each case line is the same color on every graph
    case_colors = {
        "0_100_0": "tab:blue",
        "100_0_0": "tab:orange",
        "25_25_50": "tab:green",
        "80_10_10": "tab:red",
    }

    # Specify the x-axis column (you can change this value as needed)
    x_axis_col = "Time(s)"  # For example, could be "Size(MB)" if desired.

    for method in methods:
        # Create a new figure for each method
        fig, ax = plt.subplots(figsize=(6, 5))
        
        for case in cases:
            # Build the path to the case directory
            case_path = os.path.join(root_dir, chunk_size, method, case)

            # Gather all files ending with '-Host.memspace_usage'
            file_list = [
                os.path.join(case_path, f)
                for f in os.listdir(case_path)
                if f.endswith("-Host.memspace_usage")
            ]
            file_list.sort()  # Sort for consistent ordering

            # Read data & compute the average for both time and HW columns
            avg_df = read_and_average(file_list, x_col=x_axis_col)

            # Format the case string from "x_y_z" to "(x, y, z)"
            formatted_case = "(" + ", ".join(case.split("_")) + ")"
            
            # Plot on the current figure
            ax.plot(
                avg_df[x_axis_col], 
                avg_df["avg_HW"], 
                label=formatted_case, 
                color=case_colors[case],
                linewidth=3
            )

        # Configure axis labels, grid, and legend
        ax.set_xlabel(x_axis_col)
        ax.set_ylabel("Avg Memory HighWater(MB)")
        ax.grid(True)
        ax.legend(title="Chunk Distribution\n(FO,FD,SD)")
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)

        # Set the title with each word's first letter capitalized.
        method_title = method.replace('_', ' ').title()
        plt.title(f"Memory Highwater Usage For {method_title} Method")

        # Adjust layout to prevent clipping
        plt.tight_layout()
        # Save the figure using the method name in the file name
        save_path = os.path.join(
            "/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/graphs/HPDC25",
            f"hpdc25_mem_2048_{method}.png"
        )
        plt.savefig(save_path)
        plt.show()

if __name__ == "__main__":
    main()
