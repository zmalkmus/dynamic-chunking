# =====================================
# Deduplication
# =====================================

gpu_dedup_path="${RESEARCH}/ANL/dynamic_chunking/gpu-dedup/build"

# Chunk size might need adjustment based on typical data size and desired granularity
# chunk_size=163840 # Adjust as needed for combined file sizes
# chunk_size=2048
chunk_size=512
# chunk_size=512

cd $gpu_dedup_path

# checkpoints=($miniamr_path/checkpoint_ts*)
checkpoints=($miniamr_path/dump_ts*)

# Run the deduplication tool on the sorted list of combined checkpoint files
./dedup_files \
  -a list \
  -c "$chunk_size" \
  -e 0.00000001 \
  "${checkpoints[@]}"

# =====================================
# Restore
# =====================================

# # Restore directory - create if it doesn't exist
# restore_dir="${combined_checkpoint_dir}/restored"
# mkdir -p "$restore_dir"

# restore_checkpoint=$(($num_files - 1))

# echo "Restoring combined checkpoint $restore_checkpoint (File index)"
# echo "Restoring combined checkpoint $restore_checkpoint (File index)" >> ma.out

# for i in $(seq 0 $restore_checkpoint); do
#   echo "Restoring combined file version index $i"
#   $gpu_dedup_path/restore_files $i \
#     -a tree \
#     -c "$chunk_size" \
#     "${combined_files[@]}"

# echo "Deduplication and Restore steps finished for combined checkpoints."

cd -