#!/bin/bash

# Call: raw_data_merging.sh <node>

node=$1
cd "${node}"
files=$(ls -l | awk -F' ' '{print $9}' | grep 'raw_data_*')
out_file="full_raw_dataset_${node}.csv"
tmp="out.tmp"

echo $files | while read file
do
    cat $file >> $tmp
done

header=$(cat $tmp | grep "timestamp" | head -n 1)
echo $header > $out_file
$(cat $tmp | egrep -v "timestamp|=" >> $out_file )
rm $tmp
mv $out_file ../$out_file
