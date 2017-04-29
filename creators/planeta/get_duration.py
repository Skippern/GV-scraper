#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to download time tables as PDF and calculate route durations based on relations for the routes in OpenStreetMap
from common import *

import os
import sys
import io
import logging
import requests
import json
import datetime
import time
from unidecode import unidecode


logger = logging.getLogger("GTFS_get_durations")
logging.basicConfig(filename="/var/log/GTFS/planeta-es.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

# PDFs are stored here
baseurl = "http://www.viacaoplaneta-es.com.br/destinos-e-horarios-viacao-planeta/"

debugMe = False

# List of route numbers

config = {}
with open('planeta.json', 'r') as infile:
    config = json.load(infile)

durationsList = {}
try:
    with open('durations.json', 'r') as infile:
        durationsList = json.load(infile)
except:
    pass
durationsList[u"updated"] = str(datetime.date.today())
durationsList[u"operator"] = u"Viação Planeta"
durationsList[u"network"] = u"Planeta"
durationsList[u"source"] = baseurl

for i in getLines():
    name = i[1]
    ref = i[0]
    print ref, name
    tmp = name.split(u" x ")
    origin = tmp.pop(0)
    destination = get_destination(tmp)
    origin = origin.strip()
    destination = destination.strip()
    
    print "    From:", origin
    print "    To:  ", destination
    if len(tmp) > 0:
        debug_to_screen( u"    Via: {0}".format( (tmp) ) )
    durationsList[ref] = [ get_duration(ref, origin, destination, config["query"]["bbox"]), get_duration(ref, destination, origin, config["query"]["bbox"]) ]
    print "Durations calculated ",ref, ":", durationsList[ref]
    if ref == "1" or ref == "2":
        myRef = "{0}-1".format(ref)
        durationsList[myRef] = [ get_duration(myRef, origin, destination, config["query"]["bbox"]), get_duration(myRef, destination, origin, config["query"]["bbox"]) ]
        print "Durations calculated ",myRef, ":", durationsList[myRef]

with open('durations.json', 'w') as outfile:
    json.dump(durationsList, outfile, sort_keys=True, indent=4)






