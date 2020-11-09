# APIs for features splitting into numerical and categorical sets.

# import section
import re
import pandas as pd
import datetime
from datetime import timedelta

# High Level APIs:

def get_numerical_features(df):
    df = convert_dataframe_columns_to_numeric(df.set_index('timestamp'))
    df = df.select_dtypes(exclude=['object'])
    return df.reset_index()

def get_categorical_features(df):
    df = df.set_index('timestamp')
    categorical_columns = extract_columns_types(df=df, is_numerical=False, is_categorical=True).values
    df = df.loc[:,categorical_columns]
    return df.reset_index()

# Low Level APIs:

def convert_dataframe_columns_to_numeric(df):
    return df.apply(pd.to_numeric, errors='ignore')

def extract_columns_types(df, is_numerical, is_categorical):
    df = get_not_numerical_features(df)
    columns_type = detect_columns_type(df)
    return columns_type[(columns_type['is_numerical'] == is_numerical) & (columns_type['is_categorical'] == is_categorical)]['columns']

def get_not_numerical_features(df):
    df = convert_dataframe_columns_to_numeric(df)
    return df.select_dtypes(include=['object'])

def detect_columns_type(data):
    results = pd.DataFrame(data=None, columns=['columns', 'is_numerical', 'is_categorical'])
    results['columns'] = data.columns
    is_num = []
    is_cat = []
    for column in data.columns:
        num, cat = detect_column_type(data[column])
        is_num.append(num)
        is_cat.append(cat)
    results['is_numerical'] = pd.Series(is_num)
    results['is_categorical'] = pd.Series(is_cat)
    
    return results

def detect_column_type(values):
    contains_numbers = False
    contains_chars = False
    regex = re.compile(".*[\ ,a-z,A-Z,:,!,?,\(,\),\[,\],\{,\}]+.*")
    
    for val in values.values:
        if(regex.match(str(val))):
            contains_chars = True
        else:
            contains_numbers = True
    return contains_numbers, contains_chars