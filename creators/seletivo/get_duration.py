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
from unidecode import unidecode


logger = logging.getLogger("GTFS_get_durations")
logging.basicConfig(filename="/var/log/GTFS/seletivo.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

# PDFs are stored here
baseurl = "http://ceturb.es.gov.br/"

stationList = {}

def getRefs(ref):
    ref = ref.strip()
    debug_to_screen( "Testing getRefs on {0}".format(ref) )
    stationList[ref] = [None, None]
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

config = {}
with open('seletivo.json', 'r') as infile:
    config = json.load(infile)

durationsList = {}
try:
    with open('durations.json', 'r') as infile:
        durationsList = json.load(infile)
except:
    pass
durationsList[u"updated"] = str(datetime.date.today())
durationsList[u"operator"] = u"Seletivo"
durationsList[u"network"] = u"Seletivo"
durationsList[u"source"] = baseurl

def getStations(ref):
    #    return stationList[ref]
    stations = [ None, None ]
    if ref == "1902":
        stations[0] = lower_capitalized(u"Marcilio de Noronha")
    downloadURL = "https://sistemas.es.gov.br/webservices/ceturb/onibus/api/BuscaHorarios/" + ref
    myJSON = None
    r = False
    while r == False:
        try:
            r = requests.get(downloadURL, timeout=30)
        except:
            r = False
        try:
            myJSON = json.dumps(json.loads(r.content))
        except:
            r = False
    for i in json.loads(myJSON):
        if i["Terminal_Seq"] == 1:
            stations[0] = lower_capitalized(i["Desc_Terminal"])
        elif i["Terminal_Seq"] == 2:
            stations[1] = lower_capitalized(i["Desc_Terminal"])
        else:
            debug_to_screen( "{0} - {1}".format(i["Terminal_Seq"], i["Desc_Terminal"]))
    return stations

for i in getLines():
    name = i[1]
    ref = i[0]
    origin, destination = getStations(ref)
    print ref, name
    print "    From", origin
    print "    To", destination
    for myRef in getRefs(ref):
        durationsList[myRef] = [ get_duration(myRef, origin, destination, config["query"]["bbox"]), get_duration(myRef, destination, origin, config["query"]["bbox"]) ]
        print "Durations calculated {0}: {1} / {2}".format( myRef, durationsList[myRef][0], durationsList[myRef][1] )

with open('durations.json', 'w') as outfile:
    json.dump(durationsList, outfile, sort_keys=True, indent=4)






