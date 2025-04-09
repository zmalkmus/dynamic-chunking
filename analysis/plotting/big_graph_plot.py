import thicket as tt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# =================== Test Cases ===================

# The size of the data is 1GB
# The chunk size is 512B

# The first test case is all first occurrences:
#   - Total chunks: 1024*1024*1024/512 = 2,097,152
#   - First occurrences: 2,097,152
#   - Shifted duplicates: 0
#   - Fixed duplicates: 0

# The second test case is all fixed duplicates:
#   - Total chunks: 1024*1024*1024/512 = 2,097,152
#   - First occurrences: 0
#   - Shifted duplicates: 0
#   - Fixed duplicates: 2,097,152

# The third test case is a theoretical realistic case of a mix of shifted and fixed duplicates:
#   - Total chunks: 1024*1024*1024/512 = 2,097,152
#   - First occurrences: 500,000
#   - Shifted duplicates: 1,000,000
#   - Fixed duplicates: ~500,000

# =================== Data Files ===================

# Performance Logs
all_first_occur_cali = ['../data/cases/all_first_occur/1G_floats_512_tree_output.cali']
all_fixed_dup_cali = ['../data/cases/all_fixed_duplicates/1G_floats_512_tree_output.cali']
shifted_fixed_mix_cali = ['../data/cases/shifted_fixed_mix/1G_floats_512_tree_output.cali']

# Parameters
all_first_occur_changes = '../data/cases/all_first_occur/changes.csv'
all_fixed_dup_changes = '../data/cases/all_fixed_duplicates/changes.csv'
shifted_fixed_mix_changes = '../data/cases/shifted_fixed_mix/changes.csv'

# =================== Process Data ===================

def read_cali_files(file_list):
    """
    Reads and combines multiple Caliper (.cali) files into a single DataFrame.
    """
    combined_df = pd.DataFrame()
    for filename in file_list:
        th = tt.Thicket.from_caliperreader(filename)
        df = th.dataframe
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    filtered_df = filter_and_clean_df(combined_df)
    return filtered_df

def filter_and_clean_df(df):
    """
    Filters and cleans the DataFrame:
    - Keeps only entries with 'Restore', 'Restart', or 'Diff' in the 'name' column.
    - Removes entries where 'Avg time/rank' is <= 0.001.
    - Renames columns for clarity.
    """
    # Filter to include only entries with 'Restore', 'Restart', or 'Diff' in the 'name' column
    df = df[df['name'].str.contains('Restore|Restart|Diff', regex=True)]
    
    # Remove entries where 'Avg time/rank' is zero, NaN, or very small
    df = df[df['Avg time/rank'] > 0.001]  # Exclude very small times
    
    # Keep necessary columns and rename them
    df = df[['name', 'Avg time/rank']]
    df = df.rename(columns={'name': 'Restore Method', 'Avg time/rank': 'Avg Time'})
    
    return df

def process_data():
    """
    Processes all test case data and combines them into a single DataFrame.
    Adds a 'Test Case' column to distinguish between different scenarios.
    """
    # Read and process each test case
    all_first_occur_df = read_cali_files(all_first_occur_cali)
    all_fixed_dup_df = read_cali_files(all_fixed_dup_cali)
    shifted_fixed_mix_df = read_cali_files(shifted_fixed_mix_cali)
    
    # Add a 'Test Case' column to each DataFrame
    all_first_occur_df['Test Case'] = 'All First Occurrences'
    all_fixed_dup_df['Test Case'] = 'All Fixed Duplicates'
    shifted_fixed_mix_df['Test Case'] = 'Shifted & Fixed Duplicates Mix'
    
    # Combine all DataFrames into one
    combined_df = pd.concat([
        all_first_occur_df,
        all_fixed_dup_df,
        shifted_fixed_mix_df
    ], ignore_index=True)
    
    # Save the combined DataFrame to a CSV file (optional)
    combined_df.to_csv('../data/combined_data.csv', index=False)
    
    return combined_df

# =================== Plot Data ===================

def plot_combined_graph(combined_df):
    """
    Generates a combined bar plot for all test cases.
    Ensures that the Restore Method with the largest total Avg Time appears at the top.
    """
    # Set the Seaborn style
    sns.set(style="whitegrid")
    
    # Calculate total Avg Time per Restore Method across all test cases
    total_time_per_method = combined_df.groupby('Restore Method')['Avg Time'].sum().reset_index()
    
    # Sort Restore Methods by total Avg Time in descending order
    sorted_methods = total_time_per_method.sort_values(by='Avg Time', ascending=False)['Restore Method'].tolist()
    
    # Optional: If you want to place a specific Restore Method (e.g., 'Total Time') at the top,
    # uncomment the following lines and adjust accordingly.
    # top_method = 'Total Time'  # Replace with the actual name
    # if top_method in sorted_methods:
    #     sorted_methods.remove(top_method)
    #     sorted_methods = [top_method] + sorted_methods
    
    plt.figure(figsize=(16, 12))
    
    # Create a bar plot with 'Restore Method' on the y-axis and 'Avg Time' on the x-axis
    # Use 'Test Case' as the hue to differentiate between scenarios
    sns.barplot(
        x='Avg Time',
        y='Restore Method',
        hue='Test Case',
        data=combined_df,
        palette="Set2",
        edgecolor='none',
        order=sorted_methods  # Ensures the largest total time appears at the top
    )
    
    # Customize the plot
    plt.xlabel('Restore Time (s)', fontsize=14)
    plt.ylabel('Region', fontsize=14)
    plt.title('Restore Time by Method Across Test Cases', fontsize=18)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(title='Test Case', fontsize=12, title_fontsize=13, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Save the combined plot
    plt.savefig('../graphs/combined_plot.png', dpi=300, bbox_inches='tight')
    #plt.show()

# =================== Main ===================

def main():
    """
    Main function to process data and generate the combined plot.
    """
    # Process the data
    combined_df = process_data()
    
    # Check if the combined DataFrame is empty
    if combined_df.empty:
        print("No data available to plot. Exiting.")
        return
    
    # Plot the combined graph
    plot_combined_graph(combined_df)
    
    print("All operations completed successfully.")

if __name__ == '__main__':
    main()

# =================== End of Script ===================
