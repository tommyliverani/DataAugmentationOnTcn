# APIs to extract and process Nagios data

# import section

import pandas as pd
import datetime
from datetime import timedelta
from examon.examon import ExamonQL
import numpy as np

from my_lib import date_utils as du
from my_lib import general_utils as gu
from my_lib import examon_utils as eu

# High Level API:

# It extracts data from nagios_pub in the format: (timestamp, label) where label is:
# 0 -> not_critical_data
# 1 -> critical_data
def extract_data_from_nagios(sq, node, t_start='22-04-2019 00:00:00', t_stop='29-04-2019 00:00:00', aggregation_minutes=5):
    if aggregation_minutes not in [1, 3, 5] :
        raise Exception("<aggregation_minutes> must be 1, 3 or 5")
    
    critical_states = extract_nagios_criticality_from_examon(sq=sq, node=node, t_start=t_start, t_stop=t_stop)
    nagios_N_minute_labels = generate_critical_nagios_N_minute_labels(critical_states, aggregation_minutes)
    first_timestamp = du.parse_timestamp(t_start)
    last_timestamp = du.parse_timestamp(t_stop)
    all_timestamps = du.generate_timestamps(first_timestamp, last_timestamp, minute_step=aggregation_minutes)
    all_timestamps = pd.DataFrame(data=all_timestamps, columns=['timestamp'])
    labeled_data = insert_labels(all_timestamps, nagios_N_minute_labels)
    return labeled_data

def extract_nagios_criticalities_from_labeled_data(data):
    return data[data['label'] == 1].copy()

# Low Level APIs:

# it extract Nagios criticalities of level 'states' and then selects "DONW/DRAIN/.." data
# "states" can be a comma-separated list of values between 0 and 3: e.g. states='2' or states='0,1,2'
def extract_nagios_criticality_from_examon(sq, node, t_start='22-04-2019 00:00:00', t_stop='29-04-2019 00:00:00', states='2'):
    data = make_nagios_query(sq=sq, node=node, states=states, t_start=t_start, t_stop=t_stop)
    du.remove_seconds_and_microseconds_from_timestamp(data, inplace=True)
    criticalities = select_criticalities_from_raw_data(data)
    criticalities = du.align_timestamp_to_minutes(criticalities, minutes=15).groupby('timestamp').first().reset_index()
    critical_states = criticalities[['timestamp', 'node', 'state']]
    return critical_states

def make_nagios_query(sq, node, states, t_start, t_stop):
    data = sq.SELECT('node','state') \
             .FROM('plugin_output') \
             .WHERE(plugin='nagios_pub', state=states, node=node) \
             .TSTART(t_start) \
             .TSTOP(t_stop) \
             .execute()
    data = data.df_table
    
    # preventing empty data crash
    if(data.empty):
        data = pd.DataFrame(data=None, columns=['timestamp','node','state','value']) #if no data are available, an empty df is returned
    return data

def make_nagios_query_no_state(sq, node, t_start, t_stop):
    data = sq.SELECT('node','state') \
             .FROM('plugin_output') \
             .WHERE(plugin='nagios_pub', node=node) \
             .TSTART(t_start) \
             .TSTOP(t_stop) \
             .execute()
    data = data.df_table
    
    # preventing empty data crash
    if(data.empty):
        data = pd.DataFrame(data=None, columns=['timestamp','node','state','value']) #if no data are available, an empty df is returned
    return data

# filter for real criticatilies (state=2 and description="DRAIN/DOWN/...")
def select_criticalities_from_raw_data(data):
    criticalities = data[(data['state'] == '2') & ((data['value'].str.contains("DRAIN")) | (data['value'].str.contains("DOWN")))]
    return criticalities.reset_index(drop=True)

def generate_critical_nagios_N_minute_labels(critical_states, N=5):
    _N_minute_critical = generate_data_sampling_from_15_to_N_minutes(critical_states, N)
    _N_minute_critical.loc[:,'timestamp'] = _N_minute_critical.timestamp.astype(critical_states.loc[:,'timestamp'].dtype)
    labels = create_labels(_N_minute_critical)
    return labels[['timestamp', 'label']]

def generate_data_sampling_from_15_to_N_minutes(dataframe, N=5):
    df_cloned = pd.DataFrame(data=None, columns=dataframe.columns)
    
    for index in dataframe.index:
        df_row_split = splitting_row_values_every_N_minutes(dataframe, index, N)
        df_cloned = pd.concat([df_cloned, df_row_split], ignore_index=True)
    return df_cloned

# cloning 15//N times rows to change the sampling time from 15 to N minutes 
def splitting_row_values_every_N_minutes(dataframe, index, N=5):    
    df_cloned = pd.DataFrame(data=None, columns=dataframe.columns)
    actual_date = dataframe.loc[index, 'timestamp']
     
    for new_date in du.generate_previous_dates(actual_date, how_many=15//N, minutes=N):
        new_row = copy_row_with_new_date(dataframe.loc[index], new_date)
        df_cloned = df_cloned.append(new_row , ignore_index=True)
    return df_cloned

def copy_row_with_new_date(row, new_date):
    row_copy = {'timestamp': new_date, 'node': row['node'], 'state': row['state']}
    return row_copy

# it creates labels from critical data (simple column renaming and value changing)
def create_labels(dataframe):
    df = dataframe.rename(columns={'state':'label'})
    df.loc[:,'label'] = df['label'].copy().map({'2': '1'}) # label = 1: 'fault state', label = 0: 'not fault state'
    return df

# it creates default label values (0) and then replaces critival values.
def insert_labels(all_data, critical_data):
    all_data = all_data.copy()
    pd.DataFrame.insert(all_data, loc=1, column="label", value=0, allow_duplicates=True)
    all_tss = all_data['timestamp'].unique()
    for critical_time in critical_data['timestamp']:
        if(critical_time in all_tss):
            index = all_data.index[all_data['timestamp'] == critical_time]
            all_data.loc[index, 'label'] +=1
    return all_data

# my

# Extract states of different nodes in a single extraction
def extract_states_multi_node_query(sq, nodes, number_of_nodes, state, t_start, t_stop) :
    nodes_to_analyze = gu.get_random_nodes(nodes, number_of_nodes)
    nodes_query = eu.make_multiple_nodes_query(nodes_to_analyze)
    nodes_criticalities = make_nagios_query(sq, nodes_query, state, t_start, t_stop)
    nodes, num_criticalities = np.unique(nodes_criticalities['node'], return_counts=True)
    return pd.DataFrame(data={"node": nodes, "num_criticalities": num_criticalities})


# Top function used to find best nodes: It returns the best nodes according to the given strategy 
def search_opt_non_outlier_nodes(nodes_num_criticalities_df, bottom_percentile, best_nodes_func, *best_nodes_func_specific_args) :
    
    nodes_criticalities_df = nodes_num_criticalities_df.copy().set_index('node')
    # 1. Remove outliers
    criticalities_no_outliers_df = gu.remove_top_outliers(nodes_criticalities_df, bottom_percentile)
    # 2. Get best nodes according <best_nodes_func> strategy
    best_nodes = best_nodes_func(criticalities_no_outliers_df, *best_nodes_func_specific_args)
    
    return best_nodes


# A specific function that defines a particular strategy to get best nodes
# It returns the nodes index (in the dataframe) of nodes having maximum criticalities
def max_criticalities_node(nodes_criticalities_df) :
    return nodes_criticalities_df['num_criticalities'].idxmax()

# A specific function that defines a particular strategy to get best nodes
# It returns the nodes index (in the dataframe) of nodes having maximum rising anomalies
# Nodes are pre-filtered (nodes with maximum number of criticalities are selected) to reduce computation effort to find best nodes
def max_rising_edges(nodes_criticalities, number_of_nodes_to_evaluate, number_of_nodes_to_return, sq, t_start, t_stop) :
    
    if number_of_nodes_to_evaluate < number_of_nodes_to_return :
        raise Exception('<number_of_nodes_to_evaluate> must be grater than <number_of_nodes_to_return')
      
    # 1. Extract top non outliers nodes from nodes criticalities dataframe
    nodes_to_evaluate = nodes_criticalities['num_criticalities'].nlargest(number_of_nodes_to_evaluate)
    
    # 2. Extract nagios features for choosen nodes
    nodes_criticalities_dataframes = [ns.extract_data_from_nagios(sq, node, t_start, t_stop) \
                                      for node in nodes_to_evaluate.index]
    
    # 3. Insert rising and falling anomalies
    nodes_edges_dataframes = [gu.build_edge_cols(node_df) for node_df in nodes_criticalities_dataframes]
    
    # 4. Compute the number of rising anomalies for each dataframe
    num_rising_edges = [len(np.where(edges_df['rising_anomaly'] == 1)[0]) for edges_df in nodes_edges_dataframes]
    
    # 5. Get <number_of_nodes_to_return> maximum rising anomalies nodes
    num_rising_edges_series = pd.Series(num_rising_edges, index=nodes_to_evaluate.index)
    best_nodes = num_rising_edges_series.nlargest(number_of_nodes_to_return)

    return best_nodes.index
    
