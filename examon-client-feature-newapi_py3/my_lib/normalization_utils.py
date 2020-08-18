# APIs for data normalisation in range [0,1] using MinMaxScaler()

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# High Level APIs:

def normalize_data(df):
    scaler = MinMaxScaler(feature_range=(0, 1))
    # df = df.set_index('timestamp')
    df_norm = pd.DataFrame(data=scaler.fit_transform(df), columns=df.columns)
    df = df.reset_index()
    df_norm.loc[:,'timestamp'] = df['timestamp']
    cols = df_norm.columns.tolist()
    cols.insert(0, cols.pop(cols.index('timestamp')))
    df_norm = df_norm.reindex(columns=cols)
    return df_norm

def normalize_array(arr) :
    min_max_scaler = MinMaxScaler()
    arr_norm = min_max_scaler.fit_transform(arr)
    return arr_norm.transpose()[0].flatten().tolist()