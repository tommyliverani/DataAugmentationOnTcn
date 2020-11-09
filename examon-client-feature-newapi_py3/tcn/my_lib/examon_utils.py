# APIs for the Examon-client connection

# import section

from examon.examon import Examon, ExamonQL
import pandas as pd
import numpy as np

from my_lib import general_utils as gu

# High Level APIs

def create_examon_connection():
    KAIROSDB_SERVER = '130.186.13.80'
    KAIROSDB_PORT = '3000'
    USER = 'Lpizziga' # Change with your examon-client username
    PWD = '@UqeVymf' # Change with your examon-client password

    ex = Examon(KAIROSDB_SERVER, port=KAIROSDB_PORT, user=USER, password=PWD, verbose=False, proxy=True)
    sq = ExamonQL(ex)
    
    return sq

# my

# Get all nodes from Marconi cluster
def get_all_marconi_nodes(sq) :
    marconi_nodes_df = sq.DESCRIBE(tag_key='node', where='cluster==marconi').execute()
    marconi_nodes_list_redundant = gu.flatten_series(marconi_nodes_df['tag values'])
    marconi_nodes_list = np.unique(marconi_nodes_list_redundant)
    return pd.DataFrame(data={'node' : marconi_nodes_list})

def get_metric_tag_keys_df(sq) :
    metric_tag_keys_list = sq.get_tag_keys()
    metric_names, metric_tag_keys = zip(*[(metric['name'], metric['tag keys']) for metric in metric_tag_keys_list])
    tag_keys_df_data = {'Metric name':list(metric_names), 'Tag Keys':list(metric_tag_keys)}
    return pd.DataFrame(tag_keys_df_data)

# Get all nodes having a specific plugin installed on
def get_nodes_from_plugin(sq, plugin_name) :
    plugin_nodes_df = sq.DESCRIBE(tag_key='node', where='plugin=={}'.format(plugin_name)).execute()
    plugin_nodes_list_redundant = gu.flatten_series(plugin_nodes_df['tag values'])
    plugin_nodes_list = np.unique(plugin_nodes_list_redundant)
    return pd.DataFrame(data={'node' : plugin_nodes_list})

def make_multiple_nodes_query(nodes) :
    nodes_query = ''
    for node in nodes :
        nodes_query += node + ','
    return nodes_query[:-1]