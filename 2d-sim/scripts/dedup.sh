# =====================================
# Deduplication
# =====================================

gpu_dedup_path="${RESEARCH}/dynamic_chunking/gpu-dedup/build"
# checkpoint_path="${RESEARCH}/dynamic_chunking/2d-sim/data/40772"
checkpoint_path="${RESEARCH}/dynamic_chunking/2d-sim/data/42/AMR_OFF"

chunk_size=16
cd $gpu_dedup_path

# checkpoints=($miniamr_path/checkpoint_ts*)
checkpoints=($checkpoint_path/*.dat)

# for checkpoint in "${checkpoints[@]}"; do
#   ./dedup_files \
#     -a tree \
#     -c "$chunk_size" \
#     -e 0.1 \
#     --fuzzy-hash \
#     --dtype f \
#     $checkpoint
# done

./dedup_files \
  -a tree \
  -c "$chunk_size" \
  -e 0.1 \
  --fuzzy-hash \
  --dtype f \
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