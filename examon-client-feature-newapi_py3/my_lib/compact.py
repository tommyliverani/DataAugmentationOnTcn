# APIs for data compacting (from raw format to tabular)

# import section
import pandas as pd

# High Level APIs:

def compact_features(data):
    cmp_data = pd.DataFrame(data=None, columns=['timestamp'])
    cmp_data = cmp_data.set_index('timestamp')
    
    feature_names = data['name'].unique()
    features_cmp_data = []
    for name in feature_names:
        feature_cmp_data = compact_single_feature(data[data['name'] == name]).set_index('timestamp')
        features_cmp_data.append(feature_cmp_data)
    return cmp_data.join(features_cmp_data, how='outer').reset_index()

# Low Level APIs:

def compact_single_feature(data):
    feature_name = data.iloc[0]['name']
    cmp_data = data.drop('name', axis=1)
    cmp_data.rename(columns={'value': feature_name}, inplace=True)
    return cmp_data
