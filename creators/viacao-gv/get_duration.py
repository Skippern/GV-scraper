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
routingE = "YOURS"
try:
    import osrm
    routingE = "OSRM"
except:
    pass
import overpass


logger = logging.getLogger("GTFS_get_durations")
logging.basicConfig(filename="/var/log/GTFS/viacao-gv.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

# PDFs are stored here
baseurl = "http://sistemas.vitoria.es.gov.br/redeiti/"

debugMe = False

# List of route numbers
linheList = []

config = {}
with open('viacao-gv.json', 'r') as infile:
    config = json.load(infile)

durationsList = {}
try:
    with open('durations.json', 'r') as infile:
        durationsList = json.load(infile)
except:
    pass
durationsList[u"updated"] = str(datetime.date.today())
durationsList[u"operator"] = u"Viação Grande Vitória"
durationsList[u"network"] = u"PMV"
durationsList[u"source"] = baseurl

for i in getLines():
    name = i[1]
    ref = i[0]
    tmp = name.split(u"/")
    if len(tmp) > 2 and name.find("via") < 0:
        tmp[-1] = u"{0} (Circular)".format(tmp[-1]).replace(u"(Circular) (Circular)", u"(Circular)")
    if len(tmp) == 1:
        tmp = tmp[0].split(u"via")
        origin = tmp.pop(0)
        destination = origin
    else:
        origin = tmp.pop(0)
        if tmp[0].find(u"via") > 0:
            tmp = tmp[0].split("via")
        if tmp[0] == u"" or tmp[0] == u" ":
            destination = origin
        elif tmp[-1].find(u"(Circular)") > 0:
            destination = tmp.pop(len(tmp)-2)
    #        destination = tmp.pop(len(tmp)-1)
        else:
            destination = tmp.pop(0)
    try:
        tmp = destination.split(u" ")
        tmp.remove("(Circular)")
        destination = u" ".join(tmp)
    except:
        pass
    origin = origin.strip()
    destination = destination.strip()
    
    print ref, name
    print "    From:", origin
    print "    To:  ", destination
    if len(tmp) > 0:
        debug_to_screen( "    Via: ".format( ", ".join(tmp).strip() ) )
    durationsList[ref] = [ get_duration(ref, origin, destination, config["query"]["bbox"]), get_duration(ref, destination, origin, config["query"]["bbox"]) ]
    print "Durations calculated ",ref, ":", durationsList[ref]

with open('durations.json', 'w') as outfile:
    json.dump(durationsList, outfile, sort_keys=True, indent=4)






