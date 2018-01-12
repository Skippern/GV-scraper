#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to download time tables as PDF and calculate route durations based on relations for the routes in OpenStreetMap
from common import *

import os
import sys
import io
import logging
import json
import datetime
import time
#from unidecode import unidecode
import overpass


logger = logging.getLogger("GTFS_get_durations")
logging.basicConfig(filename="/var/log/GTFS/real.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

# PDFs are stored here

if len(sys.argv) > 1:
    sys.argv.pop(0)
    routes = sys.argv

config = {}
with open('real.json', 'r') as infile:
    config = json.load(infile)

source = {}
with open('../../sources/der-es/real.json') as infile:
    source = json.load(infile)

durationsList = {}
durationsArray = []
try:
    with open('durations.json', 'r') as infile:
        durationsList = json.load(infile)
except:
    pass
durationsList[u"updated"] = str(datetime.date.today())
durationsList[u"operator"] = u"Viação Real Ita Ltda"
durationsList[u"network"] = u"Viação Real Ita"
durationsList[u"source"] = u"DER-ES"

for ref, origin, destination, via in getLines():
    print ref, origin, "x", destination 
    print u"    From:", origin
    print u"      To:", destination
    if via is not None:
        print u"     Via:", via

    dur = get_duration(ref, origin, destination, config["query"]["bbox"])
    durationsArray.append( (ref, origin, destination, via, dur ) )
    print u"Durations calculated: ", dur

durationsList['routes'] = durationsArray

with open('durations.json', 'w') as outfile:
    json.dump(durationsList, outfile, sort_keys=True, indent=4)






