# -*- coding: utf-8 -*-
"""
    Examon app example
    
    Created on Tue Jun 20 18:03:25 2017
    
    @author:francesco.beneventi@unibo.it

"""

from examon.examon import Examon

KAIROSDB_SERVER = '130.186.13.80'
KAIROSDB_PORT = '8010'

USER = ''
PWD = ''


if __name__ == '__main__':

    if USER == '':
        print "KairosDB Login:"
        USER = raw_input("username: ")
    if PWD == '':
        PWD = raw_input("password: ")
        
    # some metrics
    core_metrics = [u'AVX.ALL',
          u'C3',
          u'C3res',
          u'C6',
          u'C6res',
          u'CYCLE_ACTIVITY.STALLS_L2_PENDING',
          u'CYCLE_ACTIVITY.STALLS_LDM_PENDING',
          u'IDQ_UOPS_NOT_DELIVERED.CORE',
          u'INT_MISC.RECOVERY_CYCLES',
          u'MEM_LOAD_UOPS_RETIRED.L3_MISS',
          u'UOPS_ISSUED.ANY',
          u'UOPS_RETIRED.RETIRE_SLOTS',
          u'aperf',
          u'clk_curr',
          u'clk_ref',
          u'cpi',
          u'dT_core',
          u'freq',
          u'hsw_ep::INT_MISC:RECOVERY_CYCLES',
          u'instr',
          u'ips',
          u'load_core',
          u'mperf',
          u'temp',
          u'tsc'] 
    
    core_metrics_basic = [u'AVX.ALL',
          u'C3',
          u'C6',
          u'CYCLE_ACTIVITY.STALLS_L2_PENDING',
          u'CYCLE_ACTIVITY.STALLS_LDM_PENDING',
          u'IDQ_UOPS_NOT_DELIVERED.CORE',
          u'INT_MISC.RECOVERY_CYCLES',
          u'MEM_LOAD_UOPS_RETIRED.L3_MISS',
          u'UOPS_ISSUED.ANY',
          u'UOPS_RETIRED.RETIRE_SLOTS',
          u'aperf',
          u'clk_curr',
          u'clk_ref',
          u'hsw_ep::INT_MISC:RECOVERY_CYCLES',
          u'instr',
          u'mperf',
          u'temp',
          u'tsc'] 
    
    core_metrics_der = [
          u'C3res',
          u'C6res',
          u'cpi',
          u'freq',
          u'ips',
          u'load_core'] 
    
    
    core_metrics_counters = [u'AVX.ALL',
          u'CYCLE_ACTIVITY.STALLS_L2_PENDING',
          u'CYCLE_ACTIVITY.STALLS_LDM_PENDING',
          u'IDQ_UOPS_NOT_DELIVERED.CORE',
          u'INT_MISC.RECOVERY_CYCLES',
          u'MEM_LOAD_UOPS_RETIRED.L3_MISS',
          u'UOPS_ISSUED.ANY',
          u'UOPS_RETIRED.RETIRE_SLOTS'] 
    
    cpu_metrics = [  u'dT_cpu',
          u'erg_dram',
          u'erg_pkg',
          u'erg_units',
          u'freq_ref',
          u'pow_dram',
          u'pow_pkg',
          u'temp_pkg',
          u'tsc',
          u'uclk']
    
    
    cpu_in = [
          u'pow_dram',
          u'pow_pkg']

    # create an examon instance
    ex = Examon(KAIROSDB_SERVER, port=KAIROSDB_PORT, user=USER, password=PWD)
    
    # test node
    node = ['node061']

    # time slice (absolute)
    tstart = "10-10-2017 17:09:00"   
    tstop = "10-10-2017 21:10:00"
    
    # time slice (relative)
#    tstart = [1200,'minutes']   
#    tstop = None               
    
    # get core metrics
    metrics = ['temp']
    tags = {'org': ['cineca'], 'cluster': ['galileo'], 'plugin' : ['pmu_pub'], 'node': node, 'core':[str(i) for i in range(0,16)] }
    groupby = {'name':'tag', 'tags':['node','core']}
    aggrby = None
    core_count_series = ex.query(tstart, tstop, metrics, tags, groupby=groupby, aggrby=aggrby)
    core_count_series.to_series(flat_index=True)
    
    # get cpu metrics
    metrics = ['pow_pkg']
    tags = {'org': ['cineca'], 'cluster': ['galileo'], 'plugin' : ['pmu_pub'], 'node': node, 'cpu':[str(i) for i in range(0,2)] }
    groupby = {'name':'tag', 'tags':['node','cpu']}
    aggrby = None
    cpu_count_series = ex.query(tstart, tstop, metrics, tags, groupby=groupby, aggrby=aggrby)
    cpu_count_series.to_series(flat_index=True)
    
    # get IPMI metrics
    metrics = ['Avg_Power']
    tags = {'org': ['cineca'], 'cluster': ['galileo'], 'plugin' : ['ipmi_pub'], 'node':node }
    groupby = {'name':'tag', 'tags':['node']}
    aggrby = None
    ipmi_series = ex.query(tstart, tstop, metrics, tags, groupby=groupby, aggrby=aggrby)
    ipmi_series.to_series(flat_index=True)
    
    # get room metrics
    metrics = ['temp']
    tags = {'org': ['cineca'],  'room' : ['n']}
    groupby = {'name':'tag', 'tags':['sensorid','plugin']}
    aggrby = None
    room_series = ex.query(tstart, tstop, metrics, tags, groupby=groupby, aggrby=aggrby)
    room_series.to_series(flat_index=True)   
    
    # merge all metrics to df_ts format only
    data = ex.merge([core_count_series.df_ts, ipmi_series.df_ts, room_series.df_ts, cpu_count_series.df_ts], interp='time', dropna=True)
    
    # populate also df_table format 
    data.merge([core_count_series.df_table, ipmi_series.df_table, room_series.df_table, cpu_count_series.df_table])
      
    # time series preview
    data.df_ts.head
    
    # plot series
    data.df_ts \
        .interpolate(method='time') \
        .plot(marker='.') \
        .legend(loc='center left', bbox_to_anchor=(1, 0.5))
        
    # export to csv as time series
    data.to_csv('examon_metrics_ts.csv', epoch=True, decimal=',', shape='ts')
    
    # export to csv as table
    data.to_csv('examon_metrics_table.csv', epoch=True, decimal=',', shape='table')
    