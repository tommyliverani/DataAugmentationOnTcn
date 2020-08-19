#!/bin/bash

#SBATCH --account=IscrC_V-Match
#SBATCH --partition=gll_usr_prod
#SBATCH --error=err_slurm.txt
#SBATCH --open-mode=append
#SBATCH --ntasks=1
#SBATCH --mem=100000   # memory in Mb
#SBATCH -t 02:00:00  # time requested in hour:minute:second

python search_node.py > "./out/search_node.txt"

echo ""
echo "--- DONE ---"
