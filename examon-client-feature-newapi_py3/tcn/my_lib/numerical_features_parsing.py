# APIs for weighted average and weighted variance computing

# import section
import math
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta

from my_lib import date_utils as du

# High Level APIs

def compute_average_and_variance_on_numerical_features(data, aggregation_minutes=5):
    weighted_data = extract_weighted_data_from_timestamps(data, aggregation_minutes=aggregation_minutes)
    chunks = du.split_into_N_minute_chunks(weighted_data, N=aggregation_minutes)
    propagate_last_timestamp(chunks)
    merged_chunks = merge_chunks(chunks)
    merged_chunks = merged_chunks.set_index(["timestamp","weight"])
    result_chunks = calculate_weighted_average_and_variance(merged_chunks)
    merged_results = join_df_list(result_chunks)
    return merged_results.apply(pd.to_numeric, errors='ignore').reset_index()

# Low Level APIs

def extract_weighted_data_from_timestamps(df, aggregation_minutes=5):
    df = add_row_every_N_minute(df.copy(), N=aggregation_minutes)
    return compute_weights(df, aggregation_minutes=aggregation_minutes)

# it creates new rows with timestamps aligned to 5 minutes 
def add_row_every_N_minute(df, N=5):
    first_ts = df.iloc[0]['timestamp']
    ts_start = du.extract_first_ts_of_minutes(first_ts, minutes=N)
    ts_current = first_ts
    new_rows = []
    
    for i in df.index:
        ts_prec = ts_current
        ts_current = df.loc[i]['timestamp']
        while((ts_start + timedelta(minutes=N) < ts_current)):
            ts_start = ts_start + timedelta(minutes=N)
            if((ts_prec < ts_start) & (ts_start < ts_current)):
                cloned_row = df.loc[i].copy()
                cloned_row['timestamp'] = ts_start
                new_rows.append(cloned_row)        
        new_rows.append(df.loc[i])
    return pd.DataFrame(new_rows, columns=df.columns).reset_index(drop=True)

def compute_weights(df, aggregation_minutes=5):
    first_ts = df.iloc[0]['timestamp']
    ts_current = du.extract_first_ts_of_minutes(first_ts, minutes=aggregation_minutes)
    
    weights = []
    for i in df.index:
        ts_prec = ts_current
        ts_current = df.loc[i]['timestamp']
        weights.append(float((ts_current - ts_prec).seconds))
    
    #append the last weight
    weights.append((ts_current - ts_prec).seconds)
    
    df['weight'] = pd.Series(weights)
    return df

# the last timestamp of a chunk is the timestamp of the entire chunk
def propagate_last_timestamp(df_list):
    for i in range(len(df_list)):
        df_list[i].loc[:,'timestamp'] = df_list[i].iloc[-1]['timestamp']

def merge_chunks(chunks):
    return chunks.pop().append(chunks)

# for the whole chunk
def calculate_weighted_average_and_variance(df):
    feauture_results = []
    for feature in df.columns:
        # select a single column but in form of dataframe
        col_df = df.copy().drop(np.delete(df.columns.values,np.where(df.columns.values == feature)), axis=1) # refactoring ?
        col_df = col_df.reset_index()
        eval_feature = compute_avg_and_var(col_df, feature)
        feauture_results.append(eval_feature)
    return feauture_results

# for a single column
def compute_avg_and_var(df, column_name):
    avg_and_var = df.groupby('timestamp').apply(lambda x: get_weighted_avg_and_var(pd.to_numeric(x[column_name]), pd.to_numeric(x.weight)))
    df_results = pd.DataFrame(data=None, columns=["timestamp","avg:"+column_name,"var:"+column_name]).set_index("timestamp")
    for i in avg_and_var.index:
        df_results.loc[i,"avg:"+column_name] = avg_and_var.loc[i][0]
        df_results.loc[i,"var:"+column_name] = avg_and_var.loc[i][1]
    return df_results

def get_weighted_avg_and_var(values, weights):
    average = np.average(values, weights=weights)
    variance = np.average((values-average)**2, weights=weights)
    return average, variance

def join_df_list(df_list):
    return df_list.pop(0).join(df_list, how="outer")