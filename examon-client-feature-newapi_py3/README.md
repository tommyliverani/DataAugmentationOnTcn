# Examon Python Client for TCN

--------------------

## Prerequisites

have access to Galileo with SSH: ssh <username>@login.galileo.cineca.it
install the environment: https://git.eees.dei.unibo.it/andrea.borghesi/exadata/-/blob/master/README.md
activate the environment: conda activate env_exadata


---------------------

## Configuration

Modify the variables in parallel_extraction_launcher.py to change the target node and the start/end time

es:
target_node = 'r089c13s04' 
t_start = parse('1-10-2019 10:00:00', dayfirst=True)
t_end = parse('21-10-2020 10:00:00', dayfirst=True)


---------------------

## Execution

* 'python parallel_extraction_launcher.py' to launch multiple query in the same node
* 'bash raw_data_merging.sh <node>' in raw_data directory to merge the obtained files
 
