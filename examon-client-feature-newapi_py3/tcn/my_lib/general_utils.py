from itertools import chain
from random import sample
import pandas as pd
import numpy as np
from datetime import timedelta

from sklearn.model_selection import train_test_split

# Convert a pandas Series to a flat list
def flatten_series(series) :
    return list(chain(*series))

# Return N random nodes from a node list
def get_random_nodes(nodes, number_of_nodes) :
    nodes_idx_to_analyze = sample(range(0, len(nodes)), number_of_nodes)
    return nodes.iloc[nodes_idx_to_analyze, 0]

# Remove observations not belonging to the given percentile in terms of number of anomalies
def remove_top_outliers(criticalities_df, percentile) :
    N_percentile = np.percentile(criticalities_df['num_criticalities'], percentile)
    criticalities_no_ouliers_df = criticalities_df.loc[criticalities_df['num_criticalities'] < N_percentile]
    return criticalities_no_ouliers_df

# Return a timestamp indexed and sorted dataset from csv file
def get_timeseries_df_from_csv(fn, dir_base='') :
    full_dataset = pd.read_csv(dir_base + fn, index_col='timestamp', parse_dates=True, infer_datetime_format=True, error_bad_lines=False)
    return full_dataset.sort_values('timestamp')

# Augment observations attributes with 'is_rising_anomaly' and 'is_falling_anomaly' computed attributes
def build_edge_cols(dataset) :
    dataset_copy = dataset.copy()
    rising_edge = []
    falling_edge = []
    
    prev_label = dataset['label'].iloc[0]
    for timestamp, label in dataset['label'].iteritems() :
        if prev_label != label :
            if label == 1 :
                rising_edge.append(1.0)
                falling_edge.append(0.0)
            else :
                falling_edge.append(1.0)
                rising_edge.append(0.0)
        else :
            rising_edge.append(0.0)
            falling_edge.append(0.0)     
        
        prev_label = label
        
    dataset_copy['rising_anomaly'] = rising_edge
    dataset_copy['falling_anomaly'] = falling_edge
    
    return dataset_copy

# Merge a list of dataframe into one dataframe
def merge_dataframes(df_list) :
    columns = df_list[0].columns
    merged_data = df_list.pop()
    for df in df_list :
        merged_data = merged_data.append(df, sort=True)
    return merged_data[columns]

# Get training data, validation data and test data from dataset
def train_valid_test_split(dataset, labels_cols=-1, train_test_split_rate=0.2, train_valid_split_rate=0.2, evaluate_label=True) :
    # Convert to numpy
    last_label = min(labels_cols) if type(labels_cols) == list else labels_cols
    x = dataset.to_numpy() if evaluate_label else dataset.iloc[:,:last_label].to_numpy()
    y = dataset.iloc[:, last_label:].to_numpy() 
    print("data shape: ", x.shape)
    print("labels shape: ", y.shape)
    
    # Split into training, validation and test data
    x_train_phase, x_test, y_train_phase, y_test = train_test_split(x, y, test_size=train_test_split_rate, shuffle=False)
    x_train, x_valid, y_train, y_valid = train_test_split(x_train_phase, y_train_phase, test_size=train_valid_split_rate, shuffle=False)
    print('training data shape: ', x_train.shape)
    print('training labels shape: ', y_train.shape)
    print('validation data shape: ', x_valid.shape)
    print('validation labels shape: ', y_valid.shape)
    print('test data shape: ', x_test.shape)
    print('test labels shape: ', y_test.shape)
    
    return x_train, y_train, x_valid, y_valid, x_test, y_test

# Compute distances from next rising anomaly
def get_distances_from_next_rising_anomaly(dataset) :
    # Reverse dataset rows order
    dataset = dataset.reset_index().iloc[::-1]
    rising_anomalies = dataset[['node', 'timestamp', 'is_rising_anomaly']]
    rising_anomalies.loc[:, 'timestamp'] = pd.to_datetime(rising_anomalies.loc[:, 'timestamp'])
    
    # Compute distances from next rising anomaly
    # NOTE: distance set to -1 for last nodes observations (ones in which next rising anomaly is unknown)
    distances = []
    prev_node = rising_anomalies.iloc[0, 0]
    prev_timestamp = rising_anomalies.iloc[0, 1]
    distance = -1
    for _, (node, timestamp, is_rising_anomaly) in rising_anomalies.iterrows() :
        if is_rising_anomaly == 1 : # reset distance
            distance = 0
        elif prev_node != node : # switch node
            distance = -1
        elif distance != -1 : # Already encountered rising anomaly
            distance += (prev_timestamp - timestamp) // timedelta(minutes=5)
        
        distances.append(distance)
        
        prev_timestamp = timestamp
        prev_node = node
        
    distances.reverse()
    
    return distances

# Reduce dataset based on observations distance from next rising anomaly
def reduce_dataset_on_rising_anomaly_distances(dataset, distances, max_distance) :
    distances = np.asarray(distances)
    pos_to_drop = np.where((distances == -1) | (distances > max_distance))[0]
    reduced_dataset = dataset.reset_index().drop(labels=pos_to_drop)
    return reduced_dataset.set_index(['node', 'timestamp'])