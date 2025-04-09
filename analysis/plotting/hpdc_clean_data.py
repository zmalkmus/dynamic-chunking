import pandas as pd
import sys

def main():
    results_path = "/home/zmalk/Research/ANL/checkpoint_restore/checkpoint_restore_analysis/data/HPDC25/"
    
    # Read the test_parameters.csv file
    params_df = pd.read_csv(results_path + "test_parameters.csv", header=0)
    
    # Sometimes the file may contain extra header rows (e.g., rows where the value in 'seed' is the literal string "seed").
    # Remove such rows.
    params_df = params_df[params_df['seed'] != 'seed'].copy()
    
    # Convert chunk_size to integer (if it isn’t already)
    params_df['chunk_size'] = params_df['chunk_size'].astype(int)
    
    # Split the test parameters into separate DataFrames based on the chunk_size.
    params_1024 = params_df[params_df['chunk_size'] == 1024].reset_index(drop=True)
    params_2048 = params_df[params_df['chunk_size'] == 2048].reset_index(drop=True)
    params_4096 = params_df[params_df['chunk_size'] == 4096].reset_index(drop=True)
    
    # Define a helper function to load a result file.
    # Here we assume that each result file has no header and columns in this order:
    # method, unused1, chunk_size, unused2, runtime.
    # We then keep only the needed columns.
    def load_result_file(filename):
        df = pd.read_csv(filename, header=None)
        df.columns = ["method", "unused1", "chunk_size", "unused2", "runtime"]
        return df[["method", "chunk_size", "runtime"]].reset_index(drop=True)
    
    # Load result files corresponding to each chunk_size.
    results_1024 = load_result_file(results_path + "268435456_1024.15.dat_restore.csv")
    results_2048 = load_result_file(results_path + "268435456_2048.15.dat_restore.csv")
    results_4096 = load_result_file(results_path + "268435456_4096.15.dat_restore.csv")
    
    # Optionally check that the number of rows match for each chunk size.
    if len(params_1024) != len(results_1024):
        print("Warning: Mismatch in row count for chunk_size 1024!")
    if len(params_2048) != len(results_2048):
        print("Warning: Mismatch in row count for chunk_size 2048!")
    if len(params_4096) != len(results_4096):
        print("Warning: Mismatch in row count for chunk_size 4096!")
    
    # Combine the test parameters and result file data line by line for each chunk size.
    combined_1024 = pd.concat([params_1024.reset_index(drop=True), results_1024.reset_index(drop=True)], axis=1)
    combined_2048 = pd.concat([params_2048.reset_index(drop=True), results_2048.reset_index(drop=True)], axis=1)
    combined_4096 = pd.concat([params_4096.reset_index(drop=True), results_4096.reset_index(drop=True)], axis=1)
    
    # Stack all combined data vertically.
    final_df = pd.concat([combined_1024, combined_2048, combined_4096], ignore_index=True)
    
    # ---- Compare the two method columns and remove the second one ----
    # Because the parameters file and the results file both have a column named "method",
    # after the concatenation there will be duplicate "method" columns.
    # Find all column indices with the name "method".
    # Identify the indices for columns named "method"
    method_indices = [i for i, col in enumerate(final_df.columns) if col == "method"]

    if len(method_indices) < 2:
        print("Warning: Less than two 'method' columns found. No duplicate to remove.")
    elif len(method_indices) > 2:
        sys.exit("Error: More than two 'method' columns found. Expected exactly two.")
    else:
        first_method = final_df.iloc[:, method_indices[0]]
        second_method = final_df.iloc[:, method_indices[1]]
        if not (first_method.str.lower() == second_method.str.lower()).all():
            sys.exit("Error: The two 'method' columns do not match in all rows.")
        
        # Drop the second "method" column by index selection:
        final_df = final_df.iloc[:, [i for i in range(final_df.shape[1]) if i != method_indices[1]]]

    
    # Preview the result and save to CSV.
    print(final_df.head())
    final_df.to_csv(results_path + "combined_results.csv", index=False)

if __name__ == "__main__":
    main()
