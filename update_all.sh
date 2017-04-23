#!/bin/bash
# Run update of all routes

export back=`pwd`

cd creators
for i in *
    do echo "Working with $i"
    cd $i
    mv GTFS_get_times.log GTFS_get_times.old`date +%s`.log >/dev/null 2>&1
    ./get_duration.py
    ./get_times.py
    cat GTFS_get_times.log | grep GTFS | grep -v DEBUG > errors.txt
    cd ..
    done

cd $back
