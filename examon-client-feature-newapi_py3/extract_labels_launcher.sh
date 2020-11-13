#!/bin/bash

#SBATCH --account=IscrC_ExaData
#SBATCH --partition=gll_usr_prod
#SBATCH --ntasks=1
#SBATCH --mem=10000   # memory requested in Mb
#SBATCH -t 02:00:00  # time requested in hour:minute:second

# call: extract_labels_launcher.sh <target_node> <aggregation_minutes> <write_file_dir> 

echo "----------------------------"
echo "extract_labels_launcher.sh"
echo "----------------------------"
echo ""
echo "launching extract_labels.py"
echo ""

node=$1

t_start="18-10-2019_10:00:00"
t_stop="11-01-2020_06:36:00"

python extract_labels.py "$t_start" "$t_stop" "$@" > "./out/node_${node}_labels.txt"

echo ""
echo "--- DONE ---"
