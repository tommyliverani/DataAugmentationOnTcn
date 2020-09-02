# call: python extract_feautures.py <t_start> <t_stop> <unique_id> <target_node> <aggregation_minutes> <write_file_path>  

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import sys
from dateutil.parser import parse

from my_lib import examon_utils as eu
from my_lib import features_extraction as fe

# Function call arguments
t_start = '18-10-2019 10:00:00' if len(sys.argv) < 2 else sys.argv[1].replace("_", " ")
t_stop = '18-10-2019 11:00:00' if len(sys.argv) < 3 else sys.argv[2].replace("_", " ")
unique_id = t_start.replace(' ', '_') if len(sys.argv) < 4 else str(sys.argv[3])                                   
target_node = 'r071c14s04' if len(sys.argv) < 5 else sys.argv[4]
aggregation_minutes = 5 if len(sys.argv) < 6 else int(sys.argv[5])
write_path = './raw_data/{}'.format(target_node) if len(sys.argv) < 7 else sys.argv[6]

# Print info
print("------- extract_features.py -------", flush=True)
print("unique_id: ", unique_id, flush=True)
print("start_time: ", t_start, flush=True)
print("stop_time: ", t_stop, flush=True)
print("file_to_write: ", write_path, flush=True)
print("aggregation_minutes: ", aggregation_minutes, flush=True)
print('target_node: ', target_node, flush=True)

# # Create Examon connection
print("\ncreating examon connection..")
sq = eu.create_examon_connection()

# Extract features
print("extracting data..\n", flush=True)
raw_data = fe.extract_data_from_examon_plugins(sq, target_node, t_start, t_stop, aggregation_minutes)

# Write results to csv file
print("\nsaving result on csv file..", flush=True)
raw_data.to_csv("{}/raw_data_{}.csv".format(write_path, unique_id), index=False)
print("--- DONE --- ", flush=True)
