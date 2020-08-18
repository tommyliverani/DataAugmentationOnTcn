# APIs to extract features from the Examon-client plugin

# import section
from my_lib import date_utils as du
from my_lib import compact as ct
from my_lib import split_features as sf
from my_lib import categorical_features_parsing as cfp
from my_lib import numerical_features_parsing as nfp

import pandas as pd

# High Level APIs:

# it extract data from Ganglia and Confluent
def extract_data_from_examon_plugins(sq, node, t_start, t_stop, aggregation_minutes=5):
    print("{} - extract_data_from_examon_plugins: Start".format(du.get_curr_time()), flush=True)
    ganglia_data = extract_data_from_plugin(sq=sq, plugin_name='ganglia_pub', node=node, t_start=t_start, t_stop=t_stop, aggregation_minutes=aggregation_minutes)
    print("{} - extract_data_from_examon_plugins: Ganglia data extracted".format(du.get_curr_time()), flush=True)
    confluent_data = extract_data_from_plugin(sq=sq, plugin_name='confluent_pub', node=node, t_start=t_start, t_stop=t_stop, aggregation_minutes=aggregation_minutes)
    print("{} - extract_data_from_examon_plugins: Confluent data extracted".format(du.get_curr_time()), flush=True)
    merged_data = merge_data_on_timestamp([ganglia_data, confluent_data])
    print("{} - extract_data_from_examon_plugins: Merged Ganglia and Confluent data".format(du.get_curr_time()), flush=True)
    merged_data.dropna(inplace=True)
    return merged_data

# it extract data from a single plugin
def extract_data_from_plugin(sq, plugin_name, node, t_start, t_stop, aggregation_minutes=5):
    print("{} - extract_data_from_plugin: Start".format(du.get_curr_time()), flush=True)
    raw_data = extract_data_from_examon(sq=sq, plugin_name=plugin_name, node=node, t_start=t_start, t_stop=t_stop)
    print("{} - extract_data_from_plugin: data extracted from Examon".format(du.get_curr_time()), flush=True)
    raw_data = du.remove_microsecods_and_align_to_5_second(raw_data)
    print("{} - extract_data_from_plugin: microseconds and 5 seconds alignment done".format(du.get_curr_time()), flush=True)
    compact_data = ct.compact_features(raw_data)
    print("{} - extract_data_from_plugin: features compacted".format(du.get_curr_time()), flush=True)
    compact_data = compact_data.where(pd.notnull(compact_data), None) # substitute np.nan with None
    filled_data = fill_all_none_values(compact_data)
    numerical_data = sf.get_numerical_features(filled_data)
    print("{} - extract_data_from_plugin: numerical features extracted".format(du.get_curr_time()), flush=True)
    categorical_data = sf.get_categorical_features(filled_data)
    print("{} - extract_data_from_plugin: categorical features extracted".format(du.get_curr_time()), flush=True)
    
    categorical_parsed_data = parse_categorical_data(categorical_data.dropna(), aggregation_minutes=aggregation_minutes)
    print("{} - extract_data_from_plugin: categorical data parsed".format(du.get_curr_time()), flush=True)
    numerical_parsed_data = parse_numerical_data(numerical_data.dropna(), aggregation_minutes=aggregation_minutes)
    print("{} - extract_data_from_plugin: numerical data parsed".format(du.get_curr_time()), flush=True)
    plugin_parsed_data = merge_data_on_timestamp([numerical_parsed_data, categorical_parsed_data])
    print("{} - extract_data_from_plugin: merged data on timestamp".format(du.get_curr_time()), flush=True)
    return plugin_parsed_data
    
# Low Level APIs:

def merge_data_on_timestamp(df_list):
    dfs = []
    for df in df_list:
        dfs.append(df.set_index('timestamp'))
    
    if(len(dfs) == 0):
        return pd.DataFrame(data=None, columns=[])    
    merged_data = dfs.pop(0)
    if(len(dfs) > 0):
        merged_data = merged_data.join(dfs, how='outer').dropna().reset_index().rename(columns={df.index.name:'timestamp'})
    return merged_data
 
# it fills backwards None values (from most recent to less recent)
def fill_all_none_values(data):
    timestamps = data.loc[:, 'timestamp']
    data = data.drop('timestamp', axis=1)
    for column in data.columns:
        new_values = fill_none_column(data.loc[:,column])
        data.loc[:, column] = new_values
    data.insert(0, 'timestamp', timestamps)
    return data

# it fills a single column
def fill_none_column(data):
    cur_val = data.iloc[-1]
    new_vals = [cur_val]
    for i in range(data.shape[0]-1,-1,-1):
        if (data.iloc[i] is None):
            new_vals.append(cur_val)
        else:
            cur_val = data.iloc[i]
            new_vals.append(cur_val)
    new_vals.reverse()
    return pd.Series(new_vals)

def parse_numerical_data(numerical_data, aggregation_minutes=5):
    numerical_parsed_data = nfp.compute_average_and_variance_on_numerical_features(numerical_data, aggregation_minutes=aggregation_minutes)
    return numerical_parsed_data

def parse_categorical_data(categorical_data, aggregation_minutes=5):
    categorical_parsed_data = cfp.one_hot_encoding_categorical_data(categorical_data, aggregation_minutes=aggregation_minutes)
    return categorical_parsed_data

# real data extraction from Examon-client
def extract_data_from_examon(sq, plugin_name, node, t_start, t_stop):
    print("plugin_name: {}\nnode: {}\nt_start: {}\nt_stop: {}".format(plugin_name, node, t_start, t_stop), flush=True)
    data = sq.SELECT('*') \
             .FROM('*') \
             .WHERE(plugin=plugin_name, node=node) \
             .TSTART(t_start) \
             .TSTOP(t_stop) \
             .execute()
    data = data.df_table
    # preventing empty data crash
    if(data.empty):
        data = pd.DataFrame(data=None, columns=['timestamp','name','value']) #if no data are available, an empty df is returned
    return data[['timestamp','name','value']]

# Parallel Extracion - Doesn't work -> Incompatibility with Python3 I guess
def async_extract_data_from_examon(sq, plugin_name, node, t_start, t_stop, scheduler_address):
    print("plugin_name: {}\nnode: {}\nt_start: {}\nt_stop: {}\ndask_scheduler_address: {}" \
          .format(plugin_name, node, t_start, t_stop, scheduler_address), flush=True)
    data = sq.SELECT('*') \
             .FROM('*') \
             .WHERE(plugin=plugin_name, node=node) \
             .TSTART(t_start) \
             .TSTOP(t_stop) \
             .execute_async(address=scheduler_address)

    # preventing empty data crash
    if(data.empty):
        #if no data are available, an empty df is returned
        data = pd.DataFrame(data=None, columns=['timestamp','name','value']) 
        
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

    return data[['timestamp','name','value']]

# Parallel Extracion - Doesn't work -> Incompatibility with Python3 I guess
def async_extract_data_from_examon_old(sq, plugin_name, node, t_start, t_stop):
    BUFSIZE = 320000
    print("plugin_name: {}\nnode: {}\nt_start: {}\nt_stop: {}".format(plugin_name, node, t_start, t_stop), flush=True)
    data = sq.SELECT('*') \
             .FROM('*') \
             .WHERE(plugin=plugin_name, node=node) \
             .TSTART(t_start) \
             .TSTOP(t_stop) \
             .execute_async(n_workers=4, threads_per_worker=2, processes=True, batch_size=BUFSIZE, \
                            dashboard_address=':4040', memory_limit='0')
    
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    
    # preventing empty data crash
    if(data.empty):
        #if no data are available, an empty df is returned
        data = pd.DataFrame(data=None, columns=['timestamp','name','value']) 

    return data[['timestamp','name','value']]

# Get marconi nodes with confluent, nagios and ganglia plugins
def merge_marconi_plugin_nodes(ganglia_nodes, confluent_nodes, nagios_nodes, marconi_nodes) :
    common_nodes = marconi_nodes.copy()
    common_nodes_merge1 = common_nodes.merge(ganglia_nodes['node'], on='node', how='inner').copy()
    common_nodes_merge2 = common_nodes_merge1.merge(confluent_nodes['node'], on='node', how='inner').copy()
    return common_nodes_merge2.merge(nagios_nodes['node'], on='node', how='inner').copy()
