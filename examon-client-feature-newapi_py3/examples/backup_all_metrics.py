# -*- coding: utf-8 -*-
"""
    Script to backup all metrics in a given time period.
    
    Created on Tue Jun 20 18:03:25 2017
    
    @author:francesco.beneventi@unibo.it

"""
import os
import time
import math
from examon.examon import Examon

# START EDITING HERE

### DB Host dta
# KairosDB server IP
KAIROSDB_SERVER = 'davidefe01'
# KairosDB server port
KAIROSDB_PORT = '8083'
# DB username
USER = 'admin'
# DB password
PWD = ''

### Query info. Full reference: https://kairosdb.github.io/docs/build/html/restapi/QueryMetrics.html
# Metrics list
# List of metrics to query. Wildcards: '*' to selects all metrics 
METRICS = ['*']
# Time of the first data point 
TSTART = "29-11-2017 11:00:00"
# Time of the last data point
TSTOP = "29-11-2017 13:00:00"
# Tags narrow down the search. 
# Only metrics that include the tag and matches one of the values are returned. 
# Tags is optional:
#  - set None if no tags are needed. 
TAGS = {'org': ['e4']}
# Group by
# You can group results by specifying one or more tag names. 
# For example, if you have a node tag, grouping by node would create a resulting 
# object for each node.
# Ref: https://kairosdb.github.io/docs/build/html/restapi/TagGrouping.html
# GROUPBY is ignored when METRICS is ['*']
GROUPBY = None
# Time zone
TIME_ZONE = 'Europe/Rome'
# Path of directory where to save metrics
FILE_NAME = 'Backup_Davide'

# STOP EDITING HERE

### Buffered queries
# Chunk size per metric in ms.
# Set this parameter to automatically slice the main query in sub-queries of
# BUFSIZE milliseconds. This prevents to saturate your client memory.  
BUFSIZE = 600000
# Output file compression.
# Generated file are compressed.
# Valid options are: None, 'gzip','bz2'
COMP=None 

if __name__ == '__main__':

    if USER == '':
        print "KairosDB Login:"
        USER = raw_input("username: ")
    if PWD == '':
        PWD = raw_input("password: ")
    # create an examon instance
    ex = Examon(KAIROSDB_SERVER, port=KAIROSDB_PORT, user=USER, password=PWD, verbose=False)
    # get epoch (ms)
    tstart_epoch = ex.get_utctmp(TSTART, TIME_ZONE)
    tstop_epoch = ex.get_utctmp(TSTOP, TIME_ZONE)
    tstep = BUFSIZE
    if (tstop_epoch - tstart_epoch) < tstep:
        tstep = tstop_epoch - tstart_epoch
    # filter
    ftag = TAGS
    # metrics
    if METRICS == ['*']:
        # Get all metrics names
        metric_names = ex.query_metricsnames()['results']
        # Get all tags
        gtags = {'name':'tag', 'tags': ex.query_tagnames()['results']}
    else:
        metric_names = METRICS
        gtags = GROUPBY
    outdir = './' + FILE_NAME + '_from_' + TSTART.replace(' ','_').replace(':','') + '_to_' + TSTOP.replace(' ','_').replace(':','')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    print "\n"
    print "Querying metrics:\n %s" % metric_names
    print "\n"
    print "Time Slice: from %d to %d, total %ds" % (tstart_epoch, tstop_epoch, tstop_epoch-tstart_epoch)
    print "\n"
    print "Saving to: %s" % outdir
    print "\n"
    t0 = time.time()
    for metric in metric_names:
        print "Processing metric %d/%d" % (metric_names.index(metric) + 1, len(metric_names))
        metrics = [metric]
        tags = ftag
        groupby =  gtags
        aggrby = None
        t_delta = 0
        for t in range(tstart_epoch, tstop_epoch, tstep):
            t_sta = t + t_delta
            t_stp = t + tstep
            if t_stp > tstop_epoch:
                t_stp = tstop_epoch
            t0_rx = time.time()
            res = ex.query(long(t_sta), long(t_stp), metrics, tags, groupby=groupby, aggrby=aggrby)
            t1_rx = time.time()
            bw_meas = res.df_table.memory_usage(index=False).sum()/(t1_rx - t0_rx)
            if not math.isnan(bw_meas):
                print "Received range: from %d to %d (remaining: %d ms) - BW : %f MB/s" % (t_sta, t_stp, tstop_epoch - t_stp, bw_meas/1e6)
            else:
                print "No data for metric: %s" %  metric
                continue
            try:
                print "Saving..."
                res.df_table['timestamp'] = res.df_table['timestamp'].astype('int64', copy=False)
                if COMP == None:
                    pathname = os.path.join(outdir, res.df_table['name'][0] + '.csv') 
                elif COMP == 'gzip':
                    pathname = os.path.join(outdir, res.df_table['name'][0] + '.csv.gz')
                elif COMP == 'bz2':
                    pathname = os.path.join(outdir, res.df_table['name'][0] + '.csv.bz')
                if not os.path.isfile(pathname):
                    res.df_table.to_csv(pathname, sep=';', decimal='.', float_format='%.12f', index=False, header ='column_names', compression=COMP)
                else: 
                    res.df_table.to_csv(pathname, sep=';', decimal='.', float_format='%.12f', index=False, mode = 'a', header=False, compression=COMP)
                del res
                t_delta = 1
            except:
                continue
    t1 = time.time()
    print "Done! - Elapsed time: %fs" % (t1 - t0)







