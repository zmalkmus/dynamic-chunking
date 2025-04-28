#!/usr/bin/env bash
#PBS -l select=2:system=polaris
#PBS -l place=scatter:exclhost
#PBS -l walltime=00:10:00
#PBS -l filesystems=home:eagle:grand
#PBS -q debug
#PBS -A Veloc
#PBS -o output/test.out
#PBS -e output/test.err

# cd $PBS_O_WORKDIR

###############################
# Common Inputs / Global Params (Test Case)
###############################
num_iter=1
num_files=4
seed=42
chunk_sizes=(1024)
build_path="/home/zmalk/Research/dynamic_chunking/gpu-dedup/build"
base_output_dir="/home/zmalk/Research/dynamic_chunking/gpu-dedup/build/data"
data_path="${base_output_dir}"
dedup_approaches=('tree')
restore_checkpoint=$(num_files-1)

###############################
# CSV file for Test Parameters (one row per test case)
# This CSV file is created in the build directory.
###############################
# CSV_FILE="${build_path}/test_parameters.csv"
# echo "seed,method,num_files,data_len,chunk_size,num_chunks,dedup_case,i" > "$CSV_FILE"

###############################
# Function: Deduplicate Data
###############################
deduplicate() {
    local chunk_size="$1"
    local dedup_case="$2"
    
    # Build a space-separated list of file paths for files 0.dat to 5.dat
    local files=""
    for file in $(seq 0 $((num_files - 1))); do
        files+=" ${data_path}/${chunk_size}/${dedup_case}/${datalen}_${chunk_size}.${file}.dat"
    done

    for approach in "${dedup_approaches[@]}"; do
        echo "Deduplicating using approach '${approach}' for chunk size ${chunk_size} and dedup case ${dedup_case}"
        ./dedup_files -a "$approach" -c "$chunk_size" $files
    done
}

###############################
# Function: Restore Data
###############################
restore() {
    local chunk_size="$1"
    local dedup_case="$2"

    local num_chunks=$((datalen/chunk_size * 4))
    
    # Build the file list as in deduplication.
    local files=""
    for file in $(seq 0 $((num_files - 1))); do
        files+=" ${data_path}/${chunk_size}/${dedup_case}/${datalen}_${chunk_size}.${file}.dat"
    done

    for approach in "${dedup_approaches[@]}"; do
        for iter in $(seq 1 "$num_iter"); do
            echo "Restoring checkpoint ${restore_checkpoint} using approach '${approach}' for chunk size ${chunk_size} and dedup case ${dedup_case} (iteration ${iter})"
            ./restore_files "$restore_checkpoint" -a "$approach" -c "$chunk_size" $files
            echo "$seed,$approach,$num_files,$datalen,$chunk_size,$num_chunks,$dedup_case,$iter" >> "$CSV_FILE"
        done
    done
}

###############################
# Main Execution Loop (Test Case)
###############################
cd "$build_path"

# for i in $(seq 1 10); do
#     seed=$((RANDOM % 10000 + 1))
#     for chunk_size in "${chunk_sizes[@]}"; do
#         for dedup_case in "${dedup_cases[@]}"; do
#             echo "=============================================="
#             echo "Test: Processing chunk size ${chunk_size}, dedup case ${dedup_case}"
#             echo "=============================================="

#             generate_data "$chunk_size" "$dedup_case"
#             deduplicate "$chunk_size" "$dedup_case"
#             restore "$chunk_size" "$dedup_case"

#             # Cleanup generated files for this test case.
#             cleanup_dir="${base_output_dir}/${chunk_size}/${dedup_case}"
#             echo "Cleaning up files in ${cleanup_dir}"
#             rm -rf "${cleanup_dir}"
#         done
#     done
# done

for chunk_size in "${chunk_sizes[@]}"; do
    for dedup_case in "${dedup_cases[@]}"; do
        echo "=============================================="
        echo "Test: Processing chunk size ${chunk_size}, dedup case ${dedup_case}"
        echo "=============================================="

        generate_data "$chunk_size" "$dedup_case"
        deduplicate "$chunk_size" "$dedup_case"
        restore "$chunk_size" "$dedup_case"

        # Cleanup generated files for this test case.
        cleanup_dir="${base_output_dir}/${chunk_size}/${dedup_case}"
        echo "Cleaning up files in ${cleanup_dir}"
        rm -rf "${cleanup_dir}"
    done
done