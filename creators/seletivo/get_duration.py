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
#from unidecode import unidecode


logger = logging.getLogger("GTFS_get_durations")
logging.basicConfig(filename="/var/log/GTFS/seletivo.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

# PDFs are stored here
baseurl = "http://ceturb.es.gov.br/"

stationList = {}

def getRefs(ref):
    ref = ref.strip()
    debug_to_screen(u"Testing getRefs on {0}".format(ref) )
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
        try:
            if len(i[u"Tipo_Orientacao"]) > 0 and i[u"Tipo_Orientacao"] != u" ":
                tmp = ref + i[u"Tipo_Orientacao"]
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
durationsList[u"routes"] = []

def getStations(ref):
    stations = [  ]
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
        if i[u"Desc_Terminal"] is not None:
            stations.append(lower_capitalized(i[u"Desc_Terminal"]))
    stations = uniq(stations)
    if len(stations) < 2:
        if ref == u"1604":
            stations.append(lower_capitalized(u"Itaparica"))
        if ref == u"1902":
            stations.append(lower_capitalized(u"Marcilio de Noronha"))
    return uniq(stations)

for i in getLines():
    name = i[1]
    ref = i[0]
    stationList = getStations(ref)
#    print stationList
    print ref, name
    via = None
    for myRef in getRefs(ref):
        for oName in stationList:
            for dName in stationList:
                if oName == dName:
#                    print u"Cercular skipped: {0} -> {1}".format(oName, dName)
                    continue
                print u"    Ref:", myRef, oName, "->", dName, "=",
                duration = get_duration(myRef, oName, dName, config[u"query"][u"bbox"])
                print duration
                durationsList[u"routes"].append([ myRef, oName, dName, via, duration ])

with open('durations.json', 'w') as outfile:
    json.dump(durationsList, outfile, sort_keys=True, indent=4)






