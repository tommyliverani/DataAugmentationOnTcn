# call: python extract_labels.py <t_start> <t_stop> <target_node> <aggregation_minutes> <write_file_path>

import warnings
warnings.filterwarnings("ignore")

from examon.examon import ExamonQL
import pandas as pd
import sys
from dateutil.parser import parse

from my_lib import examon_utils as eu
from my_lib import nagios_sampling as ns

# Function call arguments
t_start = '18-10-2019 10:00:00' if len(sys.argv) < 2 else sys.argv[1].replace("_", " ")
t_stop = '11-01-2020 06:36:00' if len(sys.argv) < 3 else sys.argv[2].replace("_", " ")
target_node = 'r089c13s04' if len(sys.argv) < 4 else sys.argv[3]
aggregation_minutes = 5 if len(sys.argv) < 5 else int(sys.argv[4])
write_path = './raw_data/{}'.format(target_node) if len(sys.argv) < 6 else sys.argv[5]

# Print info
print("------- extract_labels.py -------")
print("start_time: ", t_start)
print("stop_time: ", t_stop)
print("aggregation_minutes: ", aggregation_minutes)
print("file_to_write: ", write_path)
print('target_node: ', target_node)

# # Create Examon connection
print("\ncreating examon connection..")
sq = eu.create_examon_connection()

# Extract labels
print("extracting labels..\n")
raw_data = ns.extract_data_from_nagios(sq, target_node, t_start, t_stop, aggregation_minutes=aggregation_minutes)

# Write results to csv file
print("\nsaving result on csv file..", flush=True)
raw_data.to_csv("{}/labels.csv".format(write_path), index=False)
print("--- DONE --- ", flush=True)
