import pandas as pd
from datetime import timedelta
from tensorflow.keras.utils import to_categorical

# Split a dataset having time holes into smaller dataset without time holes
def split_into_continuos_ts(dataset) :
    dataset_list = []
    partial_df = pd.DataFrame(columns=dataset.columns)

    prev_ts = dataset.iloc[0, 0]
    for _, (features) in dataset.iterrows() :
        current_ts = features['timestamp']
        # Check time hole presence
        if (current_ts - prev_ts) > timedelta(minutes=5) :
                dataset_list.append(partial_df.reset_index().iloc[:, 1:])
                partial_df = pd.DataFrame(columns=dataset.columns) 
        partial_df = partial_df.append(features)
        prev_ts = current_ts

    dataset_list.append(partial_df.reset_index().iloc[:, 1:])
    
    return dataset_list

# Add anomaly columns
def rising_edge_updating_labels(dataset, data_to_ignore_label=2) :
    updated_dataset = dataset.rename(columns={'label': 'anomaly'})

    labels = [data_to_ignore_label if bool(anomaly) & (not bool(rising_edge)) else int(anomaly) \
              for _, (anomaly, rising_edge) in updated_dataset.iloc[:, -3:-1].iterrows()]

    updated_dataset.insert(len(updated_dataset.columns), 'label', labels, allow_duplicates=True)
    
    return updated_dataset


# one-hot encode state label into three new columns: ['is_normal_state', 'is_non_rising_anomaly', 'is_rising_anomaly']
def to_categorical_label(dataset) :
    categorical_label_dataset = dataset.copy()
    categorical_labels_matrix = to_categorical(dataset['label'].to_numpy()).transpose()
    
    is_normal_state = categorical_labels_matrix[0]
    is_rising_anomaly = categorical_labels_matrix[1]
    is_non_rising_anomaly = categorical_labels_matrix[2]
    
    categorical_label_dataset.drop(labels=['label', 'anomaly', 'rising_anomaly', 'falling_anomaly'], axis=1, inplace=True)
    
    categorical_label_dataset['is_normal_state'] = is_normal_state
    categorical_label_dataset['is_non_rising_anomaly'] = is_non_rising_anomaly
    categorical_label_dataset['is_rising_anomaly'] = is_rising_anomaly
    
    return categorical_label_dataset
