import pandas as pd
from matplotlib import pyplot as plt
from datetime import timedelta, datetime

from my_lib import date_utils as du

# NOTES: 
# Bug to fix: timezone offset handling generate false timezone.
# In particular, it doesn't care about daylight savings time and winter time.
# It doesn't generate problems on the business logic. I just suggest to take into considerations while analyzing holes.

# Input: Timestamp sorted dataframe
# Output: A dataframe having <timestamp, is_hole> columns
def find_holes_in_time_series(full_dataset_sorted) :
    last_timestamp = full_dataset_sorted.index[-1]
    first_timestamp = full_dataset_sorted.index[0]
    
    # Generate all timestamps for first to last timestamp in the dataframe
    timestamps = list(du.generate_timestamps(first_timestamp, last_timestamp, 5))
    datetime_timestamps = [ts.to_pydatetime() for ts in timestamps]
    
    full_dataset_timestamps = list(full_dataset_sorted.index)
    
    # Compute holes
    holes = [1 if real_ts not in full_dataset_timestamps else 0 for real_ts in datetime_timestamps]
    timestamps_holes = pd.DataFrame(data={'timestamp': datetime_timestamps, 'hole': holes})
    
    # Show plot for analysis
    plt.plot(timestamps_holes.loc[:, 'hole'])
    
    return timestamps_holes

# Input: A dataframe having <timestamp, is_hole> columns 
# Output: A dataframe consisting of holes interval and duration
def get_holes_boundaries(holes_ts) :
    holes = list(holes_ts['hole'])
    timestamps = list(holes_ts['timestamp'])
    
    start = []
    end = []
    duration = []
    
    prev_value = holes.pop(0)
    for idx, hole in enumerate(holes) :
        if prev_value != hole :
            if hole == 1 :
                start.append(timestamps[idx])
            else :
                end.append(timestamps[idx-1])
                duration.append(end[-1] - start[-1] + timedelta(minutes=10))
            prev_value = hole
    
    return pd.DataFrame(data={'start': start, 'end': end, 'duration': duration})

# Input: previous timestamp, following_timestamp, dataset
# Output: hole filled with values that linearly grows according to previous and followring timestamp difference (Linear Interpolation)
def fill_hole(prev_ts, foll_ts, dataset) :
    new_timestamps = []
    new_data = []
    prev_data = dataset.loc[prev_ts]
    foll_data = dataset.loc[foll_ts]
    difference_ts = foll_ts - prev_ts
    num_missing = int(difference_ts / timedelta(minutes=5))
    
    
    for i in range(1, num_missing) :
        new_ts = prev_ts + (timedelta(minutes=5) * i)
        new_timestamps.append(prev_ts + (timedelta(minutes=5) * i))
        new_row = []
        
        for j, feature_value in enumerate(prev_data) :
            if j < len(prev_data) - 1 :          # Avoid 'label'
                foll_feature_value = foll_data[j]
                values_difference = foll_feature_value - feature_value
                increment = (values_difference / num_missing) * i
                new_row.append(feature_value + increment) # New feature value grows linearly depending on missing values number between holes
            else :
                new_row.append(feature_value)  # Assign previous row 'label'
            
        new_data.append(new_row)
        
    return new_timestamps, new_data

# Input: dataset
# Output: dataset with small holes filled
def fill_small_holes(dataset, u_thresh=timedelta(minutes=45)) :
    new_rows_df = pd.DataFrame(columns=dataset.columns)
    new_rows_df.index.name = 'timestamp'

    prev_ts = dataset.index[0]
    for timestamp, (data) in dataset.iterrows() :
        timestamp_difference = timestamp - prev_ts

        if timestamp_difference > timedelta(minutes=5) and timestamp_difference < u_thresh:
            new_timestamps, new_values = fill_hole(prev_ts, timestamp, dataset)
            new_df = pd.DataFrame(data=new_values, index=new_timestamps, columns=new_rows_df.columns)
            new_df.index.name = new_rows_df.index.name
            new_rows_df = new_rows_df.append(new_df)

        prev_ts = timestamp
        
    return new_rows_df

# Input: old dataset labels, receptive field length, data to ignore label value
# Output: updated labels: label = -1 when observation is less than <receptive field> steps away from an hole
def update_hole_labels(dataset, receptive_field, data_to_ignore_label=2) :
    new_labels = []
    
    prev_timestamp = dataset.index[0]
    last_hole_distance = 0
    for timestamp, data in dataset.iterrows() :
        last_seen_interval = timestamp - prev_timestamp

        if last_seen_interval > (timedelta(minutes=5)) :
            last_hole_distance = 0
        else :
            last_hole_distance += 1

        if last_hole_distance < receptive_field :
            new_labels.append(data_to_ignore_label)
        else :
            new_labels.append(data[-1])

        prev_timestamp = timestamp

    return new_labels