#!/bin/bash
#SBATCH --job-name=ht_idn
#SBATCH --time=6:00:00
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --mem=4G
#SBATCH --array=0-131

cd ~/gep_health/scripts
module load conda
source ~/.bashrc
conda activate /users/3/kula0049/.conda/envs/gdalfix

CHUNK=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" indonesia_chunks.txt)

/users/3/kula0049/.conda/envs/gdalfix/bin/python run_chunk.py $CHUNK
