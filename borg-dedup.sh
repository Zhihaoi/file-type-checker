#!/bin/bash

# Set chunker, chunk size, dedup directory, and output file from the command line
if [ $# -ne 4 ]; then
    echo "Usage: $0 <chunker(fsc, cdc)> <chunk_size(kb)> <dedup_dir> <output_file>"
    exit 1
fi
chunker=$1
chunk_size=$2
dedup_dir=$3
output_file=$4

echo -e "# $dedup_dir" >> $output_file

# Chech the chunker
if [ $chunker == "fsc" ]; then
    echo "FSC chunker"
    if [ ! -d "./repo-fsc" ]; then
        borg init --encryption=repokey ./repo-fsc
    fi

    echo -e "borg create \n"
    echo -e "# $chunk_size K" >> $output_file
    chunk_size_bytes=`expr $chunk_size \* 1024`
    echo $chunk_size_bytes
    borg create --chunker-params=fixed,$chunk_size_bytes --compression none ./repo-fsc::top $dedup_dir >> $output_file
    borg info ./repo-fsc::top >> $output_file
    rm -r ./repo-fsc

elif [ $chunker == "cdc" ]; then
    echo "CDC chunker"
    if [ ! -d "./repo-cdc" ]; then
        borg init --encryption=repokey ./repo-cdc
    fi

    chunk_size=13 
    max_chunk_size=`expr $chunk_size + 3`
    min_chunk_size=`expr $chunk_size - 3`
    echo -e "# target chunk size: $min_chunk_size $chunk_size $max_chunk_size \n" >> $output_file
    echo -e "borg create \n"
    borg create --chunker-params=buzhash,$min_chunk_size,$max_chunk_size,$chunk_size,4095 --compression none ./repo-cdc::top $dedup_dir >> $output_file
    borg info ./repo-cdc::top >> $output_file
    rm -r ./repo-cdc

else
    echo "Invalid chunker: $chunker"
    exit 1
fi