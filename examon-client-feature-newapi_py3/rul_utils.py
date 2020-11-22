import pandas as pd
from itables import show
from itables import options as opt
import numpy as np
import csv



def compute_rul(data):
	rlu=0
	last_index=0
	data['rul']=0
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
		




	
