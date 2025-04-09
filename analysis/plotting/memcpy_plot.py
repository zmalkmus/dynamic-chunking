import thicket as tt
import pandas as pd
import matplotlib.pyplot as plt

# ================ Single File Processing ================

def process_single_cali(file_path):
    """Process a single cali file and filter for relevant profiling regions."""
    th = tt.Thicket.from_caliperreader(file_path)
    df = th.dataframe

    # Identify the correct time column
    time_columns = ['Avg time/rank', 'sum#time.duration', 'time', 'total_time']
    for col in time_columns:
        if col in df.columns:
            time_col = col
            break
    else:
        raise ValueError("No appropriate time column found in dataframe.")

    # Keep relevant columns and clean data
    df = df[['name', time_col]].rename(columns={time_col: 'Avg Time'})

    # Filter for GPU and Host profiling regions
    df = df[df['name'].str.contains('GPU|Host')]

    # Map names to a simpler format
    df['Profiling Region'] = df['name'].apply(
        lambda x: 'GPU' if 'GPU' in x else ('Host' if 'Host' in x else 'Other')
    )

    # Group by profiling region and aggregate times
    grouped_df = df.groupby('Profiling Region', as_index=False).sum()
    return grouped_df

# ================ Plotting ================

def plot_single_cali(file_path, output_path):
    """Generate a bar plot comparing GPU and Host profiling regions."""
    df = process_single_cali(file_path)

    # Plotting
    plt.figure(figsize=(6, 4))
    plt.bar(df['Profiling Region'], df['Avg Time'], color=['blue', 'orange'], edgecolor='black')

    # Customize the plot
    plt.xlabel('Profiling Region', fontsize=12)
    plt.ylabel('Average Time (s)', fontsize=12)
    plt.title('Comparison of Profiling Regions', fontsize=14)

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.show()

# ================ Main ================

if __name__ == '__main__':
    cali_file = "/home/zmalk/Research/ANL/checkpoint_restore_analysis/data/memcpy_test/output.cali"  # Path to the cali file
    output_plot = "../graphs/profiling_comparison.png"  # Output plot path

    plot_single_cali(cali_file, output_plot)
    print(f"Bar plot saved to {output_plot}.")
