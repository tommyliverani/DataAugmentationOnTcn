import pandas as pd
from itables import show
from itables import options as opt
import numpy as np
import csv



def select_rul(data):
    last_node=data['node'][0]
    last_anomaly=0
    for index,row in data.iterrows():
        if data['is_rising_anomaly'][index]==1:
            last_anomaly=index
        if last_node != data['node'][index]:
            for i in range(last_anomaly+1,index):
                data=data.drop(i)
        last_node = data['node'][index]
    for i in range(last_anomaly,data.index[-1]):
                data=data.drop(i+1)
    return data
				

def compute_rul(data):
	data['rul']=0
	rlu=0
	last_index=0
	last_node=data['node'][0]
	for index,row in data.iterrows():
		if data['node'][index]!=last_node:
			last_node=data['node'][index]
			last_index=index
		if data['is_rising_anomaly'][index]==1.0:
			for i in range(last_index,index,1):
				data['rul'][i]=index-i
			last_index=index+1
		last_node=data['node'][index]
	return data


def compute_final_rul_data(path):
	full_data = pd.read_csv(path+'/final_data_full.csv')
	full_data= select_rul(full_data)
	full_data= compute_rul(full_data)
	full_data.to_csv(path+'/final_rul_data.csv')

	



		




	
