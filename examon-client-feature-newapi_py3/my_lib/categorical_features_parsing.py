# APIs for categorical transformation using the One-Hot-Encoding technique

# import section
import pandas as pd
import pytz
import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

from my_lib import date_utils as du

# High Level APIs

def one_hot_encoding_categorical_data(data, aggregation_minutes=5):
    data = allign_sampling_to_minutes(data, aggregation_minutes=aggregation_minutes)
    #data = drop_unchanged_columns(data)
    data = data.set_index('timestamp')
    
    result = pd.DataFrame(data=None, columns=None)
    encoded_data = []
    for column in data.columns:
        encoded_column = one_hot_encode_values(values=data[[column]], values_name=column)
        encoded_data.append(encoded_column)
    result = result.join(encoded_data, how='outer')
    
    # inserting timestamp in the result (first position)
    data = data.reset_index()
    result['timestamp'] = data['timestamp']
    cols = result.columns.tolist()
    cols.insert(0, cols.pop(cols.index('timestamp')))
    return result.reindex(columns=cols)

# Low Level APIs

def allign_sampling_to_minutes(data, aggregation_minutes=5):
    data = data.copy()
    tzinfo = data.iloc[0]['timestamp'].tz
    df = pd.DataFrame(data=None, columns=data.columns)
    for index in data.index:
        data.loc[index,'timestamp'] = du.extract_first_ts_of_minutes(data.loc[index,'timestamp'], minutes=aggregation_minutes)
        df = df.append(data.loc[index])
    df = df.groupby('timestamp').nth(-1).reset_index()
    if(df.iloc[0]['timestamp'].tz == None):
        timestamps = [ts.tz_localize(pytz.timezone('Greenwich')).astimezone(tzinfo) for ts in df.loc[:,'timestamp']]
        df.loc[:,'timestamp'] = timestamps
    return df

def drop_unchanged_columns(df):
    result = pd.DataFrame(data=None, columns=['timestamp'])
    result.loc[:,'timestamp'] = df.loc[:,'timestamp']
    df = df.set_index('timestamp')
    
    for column in df.columns:
        if(len(df.loc[:,column].unique()) > 1):
            result.loc[:,column] = df.loc[:,column].values
    
    return result

# values must be a pandas Dataframe with just one column!
def one_hot_encode_values(values, values_name='x'):
    enc = OneHotEncoder(handle_unknown='ignore')
    enc.fit(values)
    one_hot_labels = enc.transform(values).toarray()
    columns_names = get_columns_names(values_name, one_hot_labels.shape[1])
    return pd.DataFrame(data=one_hot_labels, columns=columns_names)

def get_columns_names(column_name, how_many):
    columns_names = []
    for i in range(how_many):
        columns_names.append(column_name+"_"+str(i))
    return columns_names

# Round categorical columns to nearest integer (0 or 1)
def round_categorical_columns(dataset) :
    rounded_categorical_series = [dataset[col_name].apply(np.round) \
                                  if not col_name.startswith('avg') and not col_name.startswith('var') \
                                  else dataset[col_name] for col_name, _ in dataset.iteritems()]

    rounded_categorical_dataset = pd.DataFrame(index=rounded_categorical_series[0].index)
    for col in rounded_categorical_series :
        rounded_categorical_dataset[col.name] = col
        
    return rounded_categorical_dataset
