# Keras (tensorflow as backend)
from tensorflow.keras.layers import Conv1D, Activation, Dropout, Input, Dense, Flatten, Add
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
import tensorflow_addons as tfa

# Python libraries
import numpy as np
import pandas as pd
from datetime import timedelta

# Build a TCN
# Source: "An Empirical Evaluation of Generic Convolutional and Recurrent Networks for Sequence Modeling" architecture for TCN.
    # Change: Dropout -> In the paper they suggest to remove a whole channel for each training step, but I preferred to apply classic dropout with rate of 0.2

# Structure: 
            # 1) Residual Block:
                # 1.1) Input
                # 1.2) Dilated Convolutional Stack:
                    # Iterate log_2(<receptive_field>) times
                    # 1.2.1) Dilated Convolutional layer (relu activation function)
                    # 1.2.2) Weights Normalization
                    # 1.2.3) Dropout
                    # 1.2.4) Residual Connection [OPTIONAL]
            # 2) Residual Connection (if not previously added)
            # 3) Flatten
            # 4) Dropout [OPTIONAL]
            # 5) Dense output layer
def build_tcn(receptive_field, n_features, kernel_size=2, use_residual_connections=False, final_dropout_rate=0) :
    dilation_rates = get_dilation_rates(receptive_field, kernel_size)
    
    #Input Layer
    X_in = Input(shape=(receptive_field, n_features))
    X = X_in
    
    # Build stack of causal dilated convolutions
    for i, dilation_rate in enumerate(dilation_rates) :
        print('--- building {} dilated convolutional block ---'.format(i+1))
        print('dilation_rate: {}'.format(dilation_rate))
        
        prev_X = X

        # Causal Dilated Convolution
        dilated_conv = Conv1D(n_features, kernel_size, padding='causal', dilation_rate=dilation_rate, activation='relu')
        # Weights Normalization
        X = tfa.layers.WeightNormalization(dilated_conv)(X)
        # Dropout
        X = Dropout(0.2)(X)
        # Residual Connection
        if use_residual_connections :
            X = Add()([X, prev_X])
        elif i == len(dilation_rates)-1:
            X = Add()([X, X_in])
    
    
    X = Flatten()(X)
    # Add final Dropout
    if final_dropout_rate > 0 :
        X = Dropout(rate=final_dropout_rate)(X)
        
    # Output Layer
    X = Dense(1, activation='sigmoid')(X)
    
    # Buld Model
    tcn = Model(inputs=X_in, outputs=X)
    
    # Compile Model
    tcn.compile(optimizer='adam', loss='binary_crossentropy')
    
    return tcn

# Print time series generator flow in order to debug time series generator
def print_generator_data_flow(generator) :
    print("number of batches: ", len(generator))
    for i in range(len(generator)):
        in_x, out_y = generator[i]
        print(i, " - in_data shape: ", in_x.shape)
        print(i, " - out_data shape: ", out_y.shape)
        print(i, '%s => %s' % (in_x, out_y))


# Build dilation_rates list for the desidered receptive_field and kernel_size
# NOTE: receptive_field must be a power of kernel_size
def get_dilation_rates(receptive_field, kernel_size) :
    dilation_rates = []
    dilation_rate = receptive_field
    while dilation_rate > 1 :
        if dilation_rate % kernel_size != 0 :
            raise Exception('get_dilation_rates: <receptive_field> must be a power of <kernel_size>')
        dilation_rate = int(dilation_rate / kernel_size)
        dilation_rates.append(dilation_rate)
    
    dilation_rates = list(reversed(dilation_rates))
    
    print('--- Dilation Rates ---')
    print(dilation_rates)
    
    return dilation_rates

# Build a mask to skip observations from training, validation and testing

# Observations to be skipped:
# * Included by default in TimeseriesGenerator : 
#     * first `timeseries_receptive_field-1` observations for inputs (the dataset)
#     * last observation for inputs (the dataset)
# * Not included by default in TimeseriesGenerator :
#     * first `timeseries_receptive_field-1` observations for new nodes
#     * last observation for each node
#     * first `timeseries_receptive_field-1` observations after a hole
#     * last observation before a hole
#     * first `timeseries_receptive_field-1` observations after ones having `is_non_rising_anomaly=1`
#     * last observation before ones having `is_non_rising_anomaly=1`

def build_skip_mask(dataset, receptive_field) :
    dataset_to_mask = dataset.reset_index()[['node', 'timestamp', 'is_non_rising_anomaly']]
    dataset_to_mask['timestamp'] = pd.to_datetime(dataset_to_mask['timestamp'])

    mask = np.ones(len(dataset_to_mask))
    prev_node, prev_timestamp = dataset_to_mask['node'][0], dataset_to_mask['timestamp'][0]

    for idx, (node, timestamp, is_non_rising_anomaly) in dataset_to_mask.iterrows() :
    #     print('idx: {}; node: {}; timestamp: {}; is_non_rising_anomaly: {}'\
    #           .format(idx, node, timestamp, is_non_rising_anomaly))

        if (prev_node != node) or \
           (timestamp - prev_timestamp > timedelta(minutes=5)) or \
           (is_non_rising_anomaly == 1) :

            if idx+receptive_field <= len(mask) :
                mask[idx:idx+receptive_field] = 0
            else :
                mask[idx:len(mask)] = 0
            if idx > 0 :
                mask[idx-1] = 0

        prev_node = node
        prev_timestamp = timestamp
        
    return mask
