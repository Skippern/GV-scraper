#!/bin/bash
# Run update of all routes

export back=`pwd`

cd creators
for i in *
    do echo "Working with $i"
    if [ $i == "README.md" ]
    then echo "$i is not a directory"
        continue
    else
    cd $i
    fi
    ./get_duration.py 2>/dev/null
    ./get_times.py 2>/dev/null
    cd ..
    done

cd $back

exit 0

for i in `find creators | grep json | grep -v times.json | grep -v durations.json`
    do echo "Generationg GTFS from $i"
    osm2gtfs --refresh-all --config $i
    done

