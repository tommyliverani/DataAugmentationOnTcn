# Call: python process_raw_data <node>

from my_lib import normalization_utils as nu
from my_lib import general_utils as gu
from my_lib import dataset_holes_utils as dhu
from my_lib import tcn_preprocessing_utils as tpu
from my_lib import categorical_features_parsing as cfp

import pandas as pd
import sys

node = sys.argv[1]
timeseries_receptive_field = 32

# Read dataset
raw_dataset = gu.get_timeseries_df_from_csv('full_raw_dataset_{}.csv'.format(node), './raw_data/').iloc[:, :-2]
labels = gu.get_timeseries_df_from_csv('labels.csv', './raw_data/{}/'.format(node))

# Extraction postprocessing
raw_dataset_no_dup = raw_dataset.reset_index().drop_duplicates(subset='timestamp').set_index('timestamp')
# raw_dataset_drop_unchanged = cfp.drop_unchanged_columns(raw_dataset_no_dup).set_index('timestamp')
normalized_dataset = nu.normalize_data(raw_dataset_no_dup).set_index('timestamp')
merged_data = normalized_dataset.join(labels, how='outer').dropna()
missing_values_dataset = dhu.fill_small_holes(merged_data)
filled_dataset = merged_data.append(missing_values_dataset).sort_values('timestamp')
rounded_categorical_dataset = cfp.round_categorical_columns(filled_dataset)
dataset_with_anomalies_edges = gu.build_edge_cols(filled_dataset)

# TCN preprocessing
dataset_rising_edges = tpu.rising_edge_updating_labels(dataset_with_anomalies_edges)
new_labels = dhu.update_hole_labels(dataset_rising_edges, timeseries_receptive_field, data_to_ignore_label=2)
dataset_rising_edges['label'] = new_labels
categorical_label_dataset = tpu.to_categorical_label(dataset_rising_edges)

# Write final dataset
categorical_label_dataset.to_csv('./final_data/final_data_{}.csv'.format(node))
