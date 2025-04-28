
{
  dir=$(pwd)

  # . clean.sh

  # ======================================
  # Generate miniAMR data
  # ======================================

  echo "Running miniAMR..."

  miniamr_path="${RESEARCH}/dynamic_chunking/miniAMR/ref"
  miniamr_data_path="${RESEARCH}/dynamic_chunking/miniAMR/ref/data"

  cd $miniamr_path

  # Test 1 Refinement on
  # mpirun -np 8 ma.x \
  #   --num_refine 3 \
  #   --refine_freq 5 \
  #   --max_blocks 4000 \
  #   --init_x 1 --init_y 1 --init_z 1 \
  #   --npx 2 --npy 2 --npz 2 \
  #   --nx 8 --ny 8 --nz 8 \
  #   --num_objects 1 \
  #   --object 2 0 -1.10 -1.10 -1.10 0.030 0.030 0.030 1.5 1.5 1.5 0.0 0.0 0.0 \
  #   --num_tsteps 40

  # mpirun -np 1 ma.x \
  #   --num_refine 3 \
  #   --refine_freq 5 \
  #   --max_blocks 4000 \
  #   --init_x 1 --init_y 1 --init_z 1 \
  #   --npx 1 --npy 1 --npz 1 \
  #   --nx 8 --ny 8 --nz 8 \
  #   --num_objects 1 \
  #   --object 2 0 -1.10 -1.10 -1.10 0.030 0.030 0.030 1.5 1.5 1.5 0.0 0.0 0.0 \
  #   --num_tsteps 40

  # Test 2  –  NO refinement
  mpirun -np 1 ma.x \
    --num_refine 0 \
    --refine_freq 5 \
    --max_blocks 4000 \
    --init_x 10 --init_y 10 --init_z 5 \
    --npx 1 --npy 1 --npz 1 \
    --nx 8 --ny 8 --nz 8 \
    --num_objects 1 \
    --object 2 0 -1.10 -1.10 -1.10 0.030 0.030 0.030 1.5 1.5 1.5 0.0 0.0 0.0 \
    --num_tsteps 40

  # mpirun -np 1 ma.x \
  #   --num_refine 0 \
  #   --refine_freq 5 \
  #   --max_blocks 2 \
  #   --init_x 2 --init_y 1 --init_z 1 \
  #   --npx 1 --npy 1 --npz 1 \
  #   --nx 8 --ny 8 --nz 8 \
  #   --num_objects 1 \
  #   --object 2 0 -1.10 -1.10 -1.10 0.030 0.030 0.030 1.5 1.5 1.5 0.0 0.0 0.0 \
  #   --num_tsteps 40

  # Test 3 - Smaller, No refinement (potentially more empty space)
  # mpirun -np 1 ma.x \
  #   --num_refine 0 \
  #   --refine_freq 5 \
  #   --max_blocks 2 \
  #   --init_x 2 --init_y 1 --init_z 1 \
  #   --npx 1 --npy 1 --npz 1 \
  #   --nx 4 --ny 4 --nz 4 \
  #   --num_objects 1 \
  #   --object 2 0 -1.10 -1.10 -1.10 0.030 0.030 0.030 1.5 1.5 1.5 0.0 0.0 0.0 \
  #   --num_tsteps 20

  # mpirun -np 1 ma.x \
  #   --num_refine 0 \
  #   --refine_freq 5 \
  #   --max_blocks 512 \
  #   --init_x 4 --init_y 4 --init_z 4 \
  #   --npx 1 --npy 1 --npz 1 \
  #   --nx 4 --ny 4 --nz 4 \
  #   --num_objects 2 \
  #   --object 2 0 -1.10 -1.10 -1.10 0.030 0.030 0.030 1.5 1.5 1.5 0.0 0.0 0.0 \
  #   --object 2 0 0.5 0.5 1.76 0.0 0.0 -0.025 0.75 0.75 0.75 0.0 0.0 0.0 \
  #   --num_tsteps 20

  # mkdir -p $miniamr_data_path

  cd $dir
} &> test.out