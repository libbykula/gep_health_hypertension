#!/bin/bash -l
#SBATCH --job-name=indo_ht
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=12:00:00
#SBATCH --mem=4gb
#SBATCH --array=0-3297
#SBATCH --output=logs/slurm-%A-%x.out

cd ~/gep_health/scripts
module load conda
source ~/.bashrc
conda activate /users/3/kula0049/.conda/envs/gdalfix

SMOD_ID=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" indonesia_smod_ids.txt)

/users/3/kula0049/.conda/envs/gdalfix/bin/python run_one.py $SMOD_ID
