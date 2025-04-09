import os
import numpy as np
import pandas as pd
import seaborn as sns

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

def process_mem_results():
    """
    Process memory high-water usage files and generate a CSV file
    with mean and std values for each test case and method.
    """
    # Base directory where memory usage results are stored
    root_dir = "/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/data/HPDC25/mem_results"
    chunk_size = "2048"

    # Define available methods and test cases.
    all_methods = ["basic", "full", "list", "tree_naive", "tree_posix", "tree_liburing_optimized"]
    cases = ["0_100_0", "25_25_50", "80_10_10", "100_0_0"]

    rows = []
    for case in cases:
        for method in all_methods:
            case_path = os.path.join(root_dir, chunk_size, method, case)
            if not os.path.exists(case_path):
                print(f"Directory does not exist: {case_path}. Skipping.")
                continue
            file_list = [
                os.path.join(case_path, f)
                for f in os.listdir(case_path)
                if f.endswith("-Host.memspace_usage")
            ]
            file_list.sort()
            mean_val, std_val = compute_mem_hw_stats(file_list)
            rows.append({
                "test_case": case,
                "method": method,
                "mean": mean_val,
                "std": std_val
            })

    df_mem = pd.DataFrame(rows)
    output_dir = "/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/csv"
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, "hpdc25_mem_stats.csv")
    df_mem.to_csv(output_csv, index=False)
    print(f"Memory stats CSV saved to {output_csv}")

def get_full_avg(file):
    """
    Read the full restore CSV file and compute the average runtime.
    Assumes the runtime values are in the 5th column (index 4).
    """
    full_df = pd.read_csv(file, header=None)
    avg_runtime = full_df[4].mean()
    return avg_runtime

def process_restore_results():
    """
    Process checkpoint restore runtime results and generate CSV files for:
      - Aggregated runtime stats (mean and std) by chunk_size, dedup_case, and method.
      - The overall full restore average.
    """
    results_path = "/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/data/HPDC25/"
    combined_file = os.path.join(results_path, "combined_results.csv")
    full_restore_file = os.path.join(results_path, "full_restore.csv")
    
    # Compute and save the full restore average runtime.
    full_avg = get_full_avg(full_restore_file)
    full_avg_df = pd.DataFrame([{"full_avg": full_avg}])
    
    output_dir = "/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/csv"
    os.makedirs(output_dir, exist_ok=True)
    output_full_avg_csv = os.path.join(output_dir, "hpdc25_full_avg.csv")
    full_avg_df.to_csv(output_full_avg_csv, index=False)
    print(f"Full restore average CSV saved to {output_full_avg_csv}")
    
    # Read the combined results CSV.
    df = pd.read_csv(combined_file, header=0)
    
    # Ensure the columns used for grouping are numeric if necessary.
    df["chunk_size"] = pd.to_numeric(df["chunk_size"], errors="coerce")
    df["runtime"] = pd.to_numeric(df["runtime"], errors="coerce")
    
    # Group by chunk_size, dedup_case, and method to compute mean and std for runtime.
    grouped = df.groupby(["chunk_size", "dedup_case", "method"])["runtime"].agg(["mean", "std"]).reset_index()
    
    output_restore_csv = os.path.join(output_dir, "hpdc25_restore_stats.csv")
    grouped.to_csv(output_restore_csv, index=False)
    print(f"Checkpoint restore stats CSV saved to {output_restore_csv}")

def main():
    # Process and output CSV files for memory usage statistics.
    process_mem_results()
    # Process and output CSV files for checkpoint restore statistics.
    process_restore_results()

if __name__ == "__main__":
    main()
