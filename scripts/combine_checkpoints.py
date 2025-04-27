import os
import sys
import glob
import re
import shutil
from collections import defaultdict
import argparse

def combine_timestep_files(input_dir, output_dir):
    """
    Combines miniAMR dump files (dump_ts*_pe*.bin) into single checkpoint files per timestep.

    Args:
        input_dir (str): Directory containing the dump_*.bin files.
        output_dir (str): Directory where combined checkpoint_*.bin files will be saved.
    """
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Regex to extract timestep and PE number
    # Assumes format dump_tsXXXX_peYYYYYY.bin
    file_pattern = re.compile(r"dump_ts(\d+)_pe(\d+)\.bin$")

    # Group files by timestep
    timestep_files = defaultdict(list)
    search_path = os.path.join(input_dir, "dump_ts*_pe*.bin")
    all_dump_files = glob.glob(search_path)

    if not all_dump_files:
        print(f"Warning: No 'dump_ts*_pe*.bin' files found in '{input_dir}'.")
        return

    print(f"Found {len(all_dump_files)} dump files in '{input_dir}'.")

    for filepath in all_dump_files:
        match = file_pattern.search(os.path.basename(filepath))
        if match:
            timestep = int(match.group(1))
            pe_rank = int(match.group(2))
            timestep_files[timestep].append({'rank': pe_rank, 'path': filepath})
        else:
            print(f"Warning: Skipping file with unexpected name format: {filepath}")

    # Process each timestep
    timesteps_processed = 0
    for timestep, files in sorted(timestep_files.items()):
        # Sort files by PE rank to ensure correct concatenation order
        files.sort(key=lambda x: x['rank'])

        output_filename = f"checkpoint_ts{timestep:04d}.bin"
        output_filepath = os.path.join(output_dir, output_filename)

        print(f"Combining {len(files)} files for timestep {timestep} into {output_filepath}...")

        try:
            with open(output_filepath, 'wb') as outfile:
                for file_info in files:
                    try:
                        with open(file_info['path'], 'rb') as infile:
                            shutil.copyfileobj(infile, outfile)
                    except IOError as e:
                        print(f"Error reading input file {file_info['path']}: {e}")
                        # Optionally remove partially created output file
                        outfile.close()
                        os.remove(output_filepath)
                        sys.exit(1) # Or continue to next timestep?

            timesteps_processed += 1
            # Optional: Verify size (sum of input sizes should match output size)
            # total_input_size = sum(os.path.getsize(f['path']) for f in files)
            # output_size = os.path.getsize(output_filepath)
            # if total_input_size != output_size:
            #     print(f"Warning: Size mismatch for timestep {timestep}. Expected {total_input_size}, got {output_size}.")

        except IOError as e:
            print(f"Error writing output file {output_filepath}: {e}")
            sys.exit(1)

    print(f"\nSuccessfully combined files for {timesteps_processed} timesteps.")
    print(f"Combined checkpoints saved in: '{output_dir}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine miniAMR per-PE dump files into per-timestep checkpoints.")
    parser.add_argument("input_dir", help="Directory containing the dump_ts*_pe*.bin files.")
    parser.add_argument("output_dir", help="Directory to save the combined checkpoint_ts*.bin files.")

    args = parser.parse_args()

    combine_timestep_files(args.input_dir, args.output_dir)