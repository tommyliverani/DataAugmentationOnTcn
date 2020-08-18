# APIs fot datetime management

# import section

import pandas as pd
from dateutil import parser
import datetime
from datetime import timedelta
import pytz

# Basic utilities for managing time

# High Level APIs

def remove_microsecods_and_align_to_5_second(data, column_name='timestamp'):
    data_copy = data.copy() # a deep copy
    
    ts = data_copy[column_name]
    ts_no_ms = []    
    for i in range(ts.shape[0]):
        new_seconds = data_copy.loc[:,column_name].iloc[i].second - (data_copy.loc[:,column_name].iloc[i].second % 5)
        ts_no_ms.append(data_copy.loc[:,column_name].iloc[i].replace(second=new_seconds, microsecond=0))
    data_copy.loc[:, column_name] = pd.Series(ts_no_ms)
    return data_copy

def split_into_N_minute_chunks(data, N=5):
    chunks = []
    df = pd.DataFrame(data=None, columns=data.columns)
    ts = extract_first_ts_of_minutes(ts=data.iloc[0]['timestamp'], minutes=N)
    for index in data.index:
        row = data.loc[index]
        if(ts + timedelta(minutes=N) >= row['timestamp']):
            df = df.append(row, ignore_index=True)
        else:
            chunks.append(df)
            df = pd.DataFrame(data=None, columns=data.columns)
            df = df.append(row, ignore_index=True)
            ts += timedelta(minutes=N)
    
    last_chunk_minutes = ((df.loc[max(df.index), 'timestamp'] - ts).seconds//60)%60
    if((last_chunk_minutes % N) == 0): # otherwise remove the incompleted chunk
        chunks.append(df)
    return chunks

def parse_timestamp(string_time):
    ts = parser.parse(string_time, dayfirst=True )
    return pd.Timestamp(ts, unit='s', tz='Europe/Rome')

def remove_seconds_and_microseconds_from_timestamp(data, column_name='timestamp', inplace=False):
    if(inplace):
        data_copy = data # the original data
    else:
        data_copy = data.copy() # a deep copy
    
    ts = data_copy[column_name]
    ts_no_ms = []    
    for i in range(ts.shape[0]):
        ts_no_ms.append(data_copy.loc[:,column_name].iloc[i].replace(second=0, microsecond=0))
    data_copy.loc[:, column_name] = pd.Series(ts_no_ms)
    return data_copy

# it generates "how_many" dates subtracting "minutes" minutes
def generate_previous_dates(datetime, how_many, minutes=0):
    dates = [datetime]
    for i in range(how_many - 1):
        dt = datetime - timedelta(minutes = minutes * (i+1))
        dates.append(dt)
    return pd.Series(dates[::-1])

# it removes excess minutes
def align_timestamp_to_minutes(data, minutes=15):
    data = data.copy()
    for index in data.index:
        
        minute_number = data.loc[index,'timestamp'].minute // minutes
        current_ts = data.loc[index,'timestamp'].replace(minute=minutes * minute_number, second=0)
        if(current_ts - data.loc[index,'timestamp'] < timedelta(minutes=15/2)):
            data.loc[index, 'timestamp'] = current_ts
        else:
            data.loc[index, 'timestamp'] = current_ts + timedelta(minutes=15)
    return data

# it generates all timestamps between "start" and "end" using "minute_step" as pace.
def generate_timestamps(start, end, minute_step=1):
    timestamps = [start]
    while (start < end):
        start += timedelta(minutes = minute_step)
        timestamps.append(start)
    return pd.Series(timestamps)

def extract_dates_from_timestamps(timestamps):
    dates = []
    for ts in timestamps:
        dates.append(ts.date())
    return pd.Series(dates)

def convert_timestamp_column_as_date(data, column_name='timestamp', new_column_name='date', inplace=False):
    if(inplace):
        data_copy = data
    else:
        data_copy = data.copy()
    data_copy.loc[:, column_name] = transform_values_from_timestamp_to_date(data_copy[column_name])
    data_copy = data_copy.rename(columns={column_name: new_column_name})
    return data_copy

def transform_values_from_timestamp_to_date(timestamps):
    df = []
    for i in range(timestamps.shape[0]):
        df.append(pd.to_datetime(timestamps.iloc[i]).date())
    return pd.Series(df)

# it extract the previous timestamp that is alligned to <minutes> minutes.
def extract_first_ts_of_minutes(ts, minutes=5):
    new_ts = pd.Timestamp(year=ts.year, month=ts.month, day=ts.day, hour=ts.hour, minute=(ts.minute // minutes) * minutes, tzinfo=ts.tz)
    return new_ts

# get current time (datetime.datetime object)
def get_curr_time() :
    now = datetime.datetime.now()
    curr_time = now.strftime("%H:%M:%S")
    return curr_time