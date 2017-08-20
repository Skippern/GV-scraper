#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to download time tables as PDF and calculate route durations based on relations for the routes in OpenStreetMap
from common import * # common functions

import os
import sys
import io
import logging
import requests
import json
import datetime
import time
#from unidecode import unidecode
import overpass


logger = logging.getLogger("GTFS_get_durations")
logging.basicConfig(filename="/var/log/GTFS/transcol.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

# PDFs are stored here
baseurl = "http://ceturb.es.gov.br/"

debugMe = False

# List of route numbers
routes = [  ]
stationList = {}

def getRefs(ref):
    ref = ref.strip()
    debug_to_screen( "Testing getRefs on {0}".format(ref) )
    stationList[ref] = [None, None]
    if ref == u"521":
        stationList[ref] = [u"Hotel Canto Sol", u"Terminal Carapina"]
    elif ref == u"544":
        stationList[ref] = [u"Hotel Canto Sol", u"Terminal Laranjeiras"]
    elif ref == u"550":
        stationList[ref] = [u"Shopping Vitória", u"Terminal Vila Velha"]
    elif ref == u"867":
        stationList[ref] = [u"Novo Horizonte", u"Terminal Carapina"]
    downloadURL = "https://sistemas.es.gov.br/webservices/ceturb/onibus/api/BuscaHorarios/" + ref
    myJSON = None
    retValue = [ unicode(ref) ]
    r = False
    while r == False:
        try:
            r = requests.get(downloadURL, timeout=30)
        except requests.exceptions.ReadTimeout as e:
            r = False
        except requests.exceptions.ConnectionError as e:
            r = False
        try:
            myJSON = json.dumps(json.loads(r.content))
        except:
            r = False
    for i in json.loads(myJSON):
        if i["Terminal_Seq"] == 1:
            stationList[ref][0] = lower_capitalized(i["Desc_Terminal"])
        elif i["Terminal_Seq"] == 2:
            stationList[ref][1] = lower_capitalized(i["Desc_Terminal"])
        else:
            debug_to_screen( "{0} - {1}".format(i["Terminal_Seq"], i["Desc_Terminal"]))
        try:
            if len(i["Tipo_Orientacao"]) > 0 and i["Tipo_Orientacao"] != u" ":
                tmp = ref + i["Tipo_Orientacao"]
                tmp = tmp.strip()
                retValue.append(tmp)
        except:
            pass
    retValue = uniq(retValue)
    return retValue

if len(sys.argv) > 1:
    sys.argv.pop(0)
    logger.info("Userdefined list: %s", ", ".join(sys.argv))
    for i in sys.argv:
        t = i.strip()
        for j in getRefs(t):
            routes.append( [ j, j ] )
    routes.sort()
    logger.info("Full route list to execute: %s", ", ".join(routes))
else:
    logger.info("Executing default list from %s", baseurl)
    for i in getLines():
        print "Getting variations for", i[0], "-", i[1]
        for j in getRefs(i[0]):
            routes.append( [ j, i[1] ] )
    routes.sort()
#    logger.info("Full route list to execute: %s", ", ".join(routes))
print "Loaded routes list, ready to start!"


config = {}
with open('transcol.json', 'r') as infile:
    config = json.load(infile)

durationsList = {}
try:
    with open('durations.json', 'r') as infile:
        durationsList = json.load(infile)
except:
    pass
durationsList[u"updated"] = str(datetime.date.today())
durationsList[u"operator"] = u"Transcol"
durationsList[u"network"] = u"Transcol"
durationsList[u"source"] = baseurl

for i in routes:
    if len(i[0]) > 3:
        ref = i[0][:3]
    else:
        ref = i[0]
    origin = stationList[ref][0]
    destination = stationList[ref][1]
    if destination == None:
        searchString = u"relation[\"type\"=\"route\"][\"route\"=\"bus\"][\"ref\"=\"{0}\"][\"from\"~\"{1}\"]({2},{3},{4},{5});out tags".format(unicode(ref), unicode(origin), config["query"]["bbox"]["s"], config["query"]["bbox"]["w"], config["query"]["bbox"]["n"], config["query"]["bbox"]["e"]).encode('ascii', 'replace').replace(u"?", u".")
        result = overpasser(searchString)
        try:
            destination = result["elements"][0]["tags"]["to"]
        except:
            try:
                destination = result["elements"]["tags"]["to"]
            except:
                destination = origin
    if origin == destination:
        logger.info("Route \"%s\" treated as circular with both origin and destination: %s", ref, origin )
    if len(i[0]) == 3:
        print "    Route:", i[0], "-", i[1]
        print "    From:", origin
        print "    To:", destination
    durationsList[i[0]] = [ get_duration(i[0], origin, destination, config["query"]["bbox"]), get_duration(i[0], destination, origin, config["query"]["bbox"]) ]
    print "Durations calculated ",i[0], ":", durationsList[i[0]]

with open('durations.json', 'w') as outfile:
    json.dump(durationsList, outfile, sort_keys=True, indent=4)






