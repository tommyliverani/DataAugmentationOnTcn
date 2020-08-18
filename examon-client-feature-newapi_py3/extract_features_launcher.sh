#!/bin/bash

#SBATCH --account=IscrC_V-Match
#SBATCH --partition=gll_usr_prod
#SBATCH --error=err_slurm.txt
#SBATCH --open-mode=append # append required to avoid different process overwrite the same error file
#SBATCH --ntasks=1
#SBATCH --mem=25000   # memory in Mb
#SBATCH -t 04:00:00  # time requested in hour:minute:second

# call: sbatch extract_features_launcher.sh <start_time> <stop_time> <unique_id> <target_node> <aggregation_minutes> <write_file_dir>

node=$4
unique_id=$3

echo "----------------------------" > "./out/${node}_${unique_id}.txt"
echo "extract_features_launcher.sh" > "./out/${node}_${unique_id}.txt"
echo "----------------------------" > "./out/${node}_${unique_id}.txt"
echo "" > "./out/${node}_${unique_id}.txt"
echo "launching extract_features.py" > "./out/${node}_${unique_id}.txt"
echo "" > "./out/${node}_${unique_id}.txt"
echo "unique_id: ${unique_id}" > "./out/${node}_${unique_id}.txt"
echo "" > "./out/${node}_${unique_id}.txt"

python extract_features.py "$@" > "./out/${node}_${unique_id}.txt"

echo ""
echo "--- DONE ---"
