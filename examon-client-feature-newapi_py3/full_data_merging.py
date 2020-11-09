import pandas as pd
import os
import numpy as np

from my_lib import general_utils as gu

# Add 'node' feature to a list of dataframes
def add_node_col_to_list(df_list, nodes) :
    df_with_nodes_list = []
    for i in range(len(df_list)) :
        df = df_list[i]
        df.insert(0, 'node', np.repeat(nodes[i], len(df)))
        df_with_nodes_list.append(df)
    return df_with_nodes_list


# Get data to merge filenames
data_to_merge_dir = os.getcwd() + '/final_data/'
filenames = [fn for fn in os.listdir(data_to_merge_dir) if fn.startswith('final_data_') and 'full' not in fn]

# Read data
df_list = [gu.get_timeseries_df_from_csv(fn, data_to_merge_dir) for fn in filenames]
nodes = [fn.split('_')[2][:-4] for fn in filenames]

# Add node column to dataframes
df_with_nodes_list = add_node_col_to_list(df_list, nodes)

# Concatenate dataframes and remove columns containing NaN values
final_data = gu.merge_dataframes(df_with_nodes_list).dropna(axis=1)

# Write final data
final_data.to_csv(data_to_merge_dir + 'final_data_full.csv')


