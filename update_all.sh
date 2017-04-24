#!/bin/bash
# Run update of all routes

export back=`pwd`

cd creators
for i in *
    do echo "Working with $i"
    cd $i
    ./get_duration.py
    ./get_times.py
    cd ..
    done

cd $back
