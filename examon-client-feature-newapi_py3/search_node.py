from examon.examon import ExamonQL
import pandas as pd
import numpy as np

from my_lib import examon_utils as eu
from my_lib import nagios_sampling as ns
from my_lib import general_utils as gu
from my_lib import features_extraction as fe

sq = eu.create_examon_connection()

t_start='18-10-2019 10:00:00'
t_stop='11-01-2020 06:36:00'


# Find common Marconi's nodes from ganglia, confluent and nagios
ganglia_nodes = eu.get_nodes_from_plugin(sq, 'ganglia_pub')
print("ganglia nodes extracted", flush=True)
confluent_nodes = eu.get_nodes_from_plugin(sq, 'confluent_pub')
print("confluent nodes extracted", flush=True)
nagios_nodes = eu.get_nodes_from_plugin(sq, 'nagios_pub')
print("nagios nodes extracted", flush=True)
marconi_nodes = eu.get_all_marconi_nodes(sq)
print("marconi nodes extracted", flush=True)

common_nodes = fe.merge_marconi_plugin_nodes(ganglia_nodes, confluent_nodes, nagios_nodes, marconi_nodes)
print("common nodes found", flush=True)

# Extract states from Examon using nagios
nodes_num_criticalities_df = ns.extract_states_multi_node_query(sq, common_nodes, len(common_nodes), '2', t_start, t_stop)
print("states extracted and filtered from nagios", flush=True)

# Extract best nodes in terms of number of criticalities
nodes_to_model = ns.search_opt_non_outlier_nodes(nodes_num_criticalities_df, 96, ns.max_rising_edges, 100, 20, sq, t_start, t_stop)

print(nodes_to_model, flush=True)

