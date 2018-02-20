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

def getRefs(ref, config):
    ref = ref.strip()
    debug_to_screen(u"Testing getRefs on {0}".format(ref) )
    stationList[ref] = []
    if ref == u"521":
        stationList[ref] = [u"Hotel Canto Sol", u"Terminal Carapina"]
    elif ref == u"544":
        stationList[ref] = [u"Hotel Canto Sol", u"Terminal Laranjeiras"]
    elif ref == u"550":
        stationList[ref] = [u"Shopping Vitória", u"Terminal Vila Velha"]
    elif ref == u"842":
        stationList[ref] = [u"Sesi", u"Terminal Laranjeiras"]
    elif ref == u"867":
        stationList[ref] = [u"Novo Horizonte", u"Terminal Carapina"]
    elif ref == u"898":
        stationList[ref] = [u"Terminal Laranjeiros", u"José de Anchieta"]
    elif ref == u"899":
        stationList[ref] = [u"Terminal Carapina", u"Castelândia"] 
    elif ref == u"906":
        stationList[ref] = [u"Terminal Campo Grande", u"Soteco"] 
    elif ref == u"914":
        stationList[ref] = [u"Terminal Campo Grande", u"Vila Bethânia"]
    elif ref == u"916":
        stationList[ref] = [u"Terminal Campo Grande", u"Arlindo Vilaschi"]
    elif ref == u"917":
        stationList[ref] = [u"Terminal Campo Grande", u"Areinha"]
    elif ref == u"927":
        stationList[ref] = [u"Terminal São Torquato", u"Viana"]
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
        stationList[ref].append(lower_capitalized(i[u"Desc_Terminal"]))
        try:
            if len(i[u"Tipo_Orientacao"]) > 0 and i[u"Tipo_Orientacao"] != u" ":
                tmp = ref + i[u"Tipo_Orientacao"]
                tmp = tmp.strip()
                retValue.append(tmp)
        except:
            pass
    stationList[ref] = uniq(stationList[ref])
    if len(stationList) < 2:
        print "Getting destination from Overpass:",
        searchString = u"relation[\"type\"=\"route\"][\"route\"=\"bus\"][\"ref\"=\"{0}\"][\"from\"~\"{1}\"]({2},{3},{4},{5});out tags".format(unicode(ref), unicode(stationList[ref][0]), config["query"]["bbox"]["s"], config["query"]["bbox"]["w"], config["query"]["bbox"]["n"], config["query"]["bbox"]["e"]).encode('ascii', 'replace').replace(u"?", u".")
        result = overpasser(searchString)
        try:
            stationList[ref].append(result[u"elements"][0][u"tags"][u"to"])
            print result[u"elements"][0][u"tags"][u"to"]
        except:
            try:
                stationList[ref].append(result[u"elements"][u"tags"][u"to"])
                print result[u"elements"][u"tags"][u"to"]
            except:
                print "failed result"
                pass
    stationList[ref] = uniq(stationList[ref])
    retValue = uniq(retValue)
    return retValue

config = {}
with open('transcol.json', 'r') as infile:
    config = json.load(infile)

if len(sys.argv) > 1:
    sys.argv.pop(0)
    logger.info(u"Userdefined list: %s", ", ".join(sys.argv))
    for i in sys.argv:
        t = i.strip()
        for j in getRefs(t, config):
            routes.append( [ j, j ] )
    routes.sort()
    logger.info(u"Full route list to execute: %s", ", ".join(routes))
else:
    logger.info(u"Executing default list from %s", baseurl)
    for i in getLines():
        print u"Getting variations for", i[0], "-", i[1]
        for j in getRefs(i[0], config):
            routes.append( [ j, i[1] ] )
    routes.sort()
#    logger.info("Full route list to execute: %s", ", ".join(routes))
print u"Loaded routes list, ready to start!"

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
durationsList[u"routes"] = []


for i in routes:
    if len(i[0]) > 3:
        ref = i[0][:3]
    else:
        ref = i[0]
    print len(stationList[ref]), ref, stationList[ref]
    if len(stationList[ref]) > 2:
        logger.warning("WARNING: %s have more than 2 start/end positions defined by CETURB, investigate", ref)
    elif len(stationList[ref]) < 2:
        logger.info("%s is circular or have no defined departur times", ref)
    origin = stationList[ref][0]
    if len(stationList[ref]) > 1:
        destination = stationList[ref][1]
    else:
        destination = origin
    if destination == None:
        searchString = u"relation[\"type\"=\"route\"][\"route\"=\"bus\"][\"ref\"=\"{0}\"][\"from\"~\"{1}\"]({2},{3},{4},{5});out tags".format(unicode(ref), unicode(origin), config["query"]["bbox"]["s"], config["query"]["bbox"]["w"], config["query"]["bbox"]["n"], config["query"]["bbox"]["e"]).encode('ascii', 'replace').replace(u"?", u".")
        result = overpasser(searchString)
        try:
            destination = result[u"elements"][0][u"tags"][u"to"]
        except:
            try:
                destination = result[u"elements"][u"tags"][u"to"]
            except:
                destination = origin
    if origin == destination:
        logger.info(u"Route \"%s\" treated as circular with both origin and destination: %s", ref, origin )
    if len(i[0]) == 3:
        print u"    Route:", i[0], "-", i[1]
#        print u"    From:", origin
#        print u"    To:", destination
#    durationsList[i[0]] = [ get_duration(i[0], origin, destination, config[u"query"][u"bbox"]), get_duration(i[0], destination, origin, config[u"query"][u"bbox"]) ]
#    print u"Durations calculated ",i[0], u":", durationsList[i[0]]
    for j in stationList[ref]:
        for k in stationList[ref]:
            duration = get_duration(i[0], j, k, config[u"query"][u"bbox"])
            if destination == origin:
                print i[0], "-", j, "->", k, "=", duration
            if j == k and duration < 0:
                continue
            print i[0], "-", j, "->", k, "=", duration
            durationsList[u"routes"].append( [i[0], j, k, None, duration] )

with open('durations.json', 'w') as outfile:
    json.dump(durationsList, outfile, sort_keys=True, indent=4)






