# =====================================
# Deduplication
# =====================================

gpu_dedup_path="${RESEARCH}/dynamic_chunking/gpu-dedup/build"

# chunk_size=10000
# chunk_size=1280
# chunk_size=512 #(4*4*4)*8
chunk_size=16
cd $gpu_dedup_path

# checkpoints=($miniamr_path/checkpoint_ts*)
checkpoints=($miniamr_path/dump_ts*)
# checkpoints=(/home/zmalk/Research/dynamic_chunking/gpu-dedup/build/data/1024/100_0_0/*)

for checkpoint in "${checkpoints[@]}"; do
  ./dedup_files \
    -a tree \
    -c "$chunk_size" \
    -e 0.00001 \
    --fuzzy-hash \
    --dtype d \
    $checkpoint
done

# ./dedup_files \
#   -a tree \
#   -c "$chunk_size" \
#   -e 0.01 \
#   --fuzzy-hash \
#   --dtype d \
#   "${checkpoints[@]}"

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