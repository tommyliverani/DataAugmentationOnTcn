#!/usr/bin/python

# call: python parallel_extraction_launcher.py <days_interval> <hours_interval> <minutes_interval> <target_node> <aggregation_minutes>
from my_lib import date_utils as du
from my_lib import examon_utils as eu

from dateutil.parser import parse
import datetime
from datetime import timedelta
import subprocess
import sys
import os

# NOTE: This way of execute parallel extraction causes multiple connection to examon. It could result in examon congestion and/or connection to be refused.


# Useful function to avoid useless data extraction and trasformation if already extracted and trasformed
def check_file_in_dir(unique_id, target_node) :
    raw_data_dir = os.getcwd() + "/raw_data/{}".format(target_node)
    files = os.listdir(raw_data_dir)
    ids = [fn.split('_')[2] + '_' + fn.split('_')[3][:-4].replace(':', '-') for fn in files if len(fn.split('_')) > 5]
    return unique_id.replace(':', '-') not in ids 

# Function call parameters
days = 0 if len(sys.argv) < 2 else int(sys.argv[1])
hours = 3 if len(sys.argv) < 3 else int(sys.argv[2])
minutes = 0 if len(sys.argv) < 4 else int(sys.argv[3])

target_node = 'r089c13s04' if len(sys.argv) < 5 else sys.argv[4]
aggregation_minutes = "5" if len(sys.argv) < 6 else sys.argv[5]


# Fixed parameters
write_files_dir = "./raw_data/{}".format(target_node)
t_start = parse('18-10-2019 10:00:00', dayfirst=True)
t_end = parse('11-01-2020 06:36:00', dayfirst=True)

# Compute list of start time extraction for parallel extraction
timestamps = []
while(t_start < t_end):
    timestamps.append(t_start)
    t_start += timedelta(days=days, hours=hours, minutes=minutes)

for start in timestamps:
    stop = start + timedelta(days=days, hours=hours+1, minutes=minutes)
    unique_id = start.strftime('%d-%m-%Y_%H-%M-%S')
    print("node", target_node, ": start:", start.strftime('%d-%m-%Y_%H:%M:%S'), "->", "stop:", stop.strftime('%d-%m-%Y_%H:%M:%S'))
    # Launch extraction with sbatch (slurm) 
    if check_file_in_dir(unique_id, target_node) :
        subprocess.run(["sbatch", "extract_features_launcher.sh", start.strftime('%d-%m-%Y_%H:%M:%S'), stop.strftime('%d-%m-%Y_%H:%M:%S'), unique_id, target_node, aggregation_minutes, write_files_dir])

print("-- DONE --")
