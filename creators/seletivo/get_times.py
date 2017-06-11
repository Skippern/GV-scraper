#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to download time tables as PDF and calculate route durations based on relations for the routes in OpenStreetMap
from common import *
from feriados import *

import os
import sys
import io
import logging
import requests
import json
import datetime
import time
from unidecode import unidecode


logger = logging.getLogger("GTFS_get_times")
logging.basicConfig(filename="/var/log/GTFS/seletivo.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

cal = EspiritoSanto()

# PDFs are stored here
baseurl = "https://ceturb.es.gov.br/"

debugMe = True

# List of route numbers

config = {}
with open('seletivo.json', 'r') as infile:
    config = json.load(infile)

durationsList = {}
try:
    with open('durations.json', 'r') as infile:
        durationsList = json.load(infile)
except:
    pass
myRoutes = {}
myRoutes[u"updated"] = str(datetime.date.today())
myRoutes[u"operator"] = u"Seletivo"
myRoutes[u"network"] = u"Seletivo"
myRoutes[u"source"] = baseurl
myRoutes[u"blacklist"] = []
myRoutes[u"routes"] = {}

def getTimes(ref):
    downloadURL = "https://sistemas.es.gov.br/webservices/ceturb/onibus/api/BuscaHorarios/" + ref
    myJSON = None
    myReturn = {}
    myReturn[u"Stations"] = {}
    myReturn[ref] = {}
    myReturn[ref]["Mo-Fr"] = {}
    myReturn[ref]["Sa"] = {}
    myReturn[ref]["Su"] = {}
    myReturn[ref]["Ex"] = {}
    for rr in myReturn[ref]:
        myReturn[ref][rr]["Ida"] = []
        myReturn[ref][rr]["Volta"] = []
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
        nuRef = None
        if len(i["Tipo_Orientacao"]):
            nuRef = ref + i["Tipo_Orientacao"]
            nuRef = nuRef.strip()
            try:
                test = myReturn[nuRef]
            except:
                myReturn[nuRef] = {}
                myReturn[nuRef]["Mo-Fr"] = {}
                myReturn[nuRef]["Sa"] = {}
                myReturn[nuRef]["Su"] = {}
                myReturn[nuRef]["Ex"] = {}
                for rr in myReturn[nuRef]:
                    myReturn[nuRef][rr]["Ida"] = []
                    myReturn[nuRef][rr]["Volta"] = []
        else:
            nuRef = ref
        day = None
        if i["TP_Horario"] == 1:
            day = "Mo-Fr"
        elif i["TP_Horario"] == 2:
            day = "Sa"
        elif i["TP_Horario"] == 3:
            day = "Su"
        elif i["TP_Horario"] == 4:
            day = "Ex"
        else:
            debug_to_screen( unicode(i["Descricao_Hora"]) )
        direction = None
        if i["Terminal_Seq"] == 2:
            direction = "Ida"
        elif i["Terminal_Seq"] == 1:
            direction = "Volta"
        myReturn[nuRef][day][direction].append(i["Hora_Saida"])
        myReturn["Stations"][direction] = lower_capitalized(i["Desc_Terminal"])
    return myReturn

def getObservations(ref):
    downloadURL = "https://sistemas.es.gov.br/webservices/ceturb/onibus/api/BuscaHorarioObse/" + ref
    myJSON = None
    myObs = []
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
        debug_to_screen( u"{0} - {1}".format(unicode(i["Tipo_Orientacao"]), unicode(i["Descricao_Orientacao"])) )
        myObs.append( [ i["Tipo_Orientacao"], i["Descricao_Orientacao"] ] )
    return myObs

for i in getLines():
    myRefs = []
    myTimes = {}
    ref = str(i[0])
    myRefs.append(ref)
    name = i[1]
    print ref, name
    logger.debug("Gathering times for route %s: %s", ref, name)
    myTimes = getTimes(ref)
    myObs = getObservations(ref)
    for j in myObs:
        tmp = ref + j[0]
        myRefs.append(tmp)
    try:
        test = myTimes["Stations"]["Volta"]
    except:
        myTimes["Stations"]["Volta"] = myTimes["Stations"]["Ida"]
    try:
        test = myTimes["Stations"]["Ida"]
    except:
        myTimes["Stations"]["Ida"] = myTimes["Stations"]["Volta"]
    for ref in myRefs:
        try:
            durations = durationsList[ref]
        except:
            durations = [ -10, -10 ]
        if durations[0] < 0 and durations[1] < 0:
            myRoutes[u"blacklist"].append(ref)
            logger.info("%s added to Blacklist", ref)
            continue
        myDays = [ u"Mo-Fr", u"Sa", u"Su", u"Ex" ]
        for d in myDays:
            if d == u"Mo-Fr" and len(myTimes[ref]["Ex"]["Ida"]) > 0:
                create_json(myRoutes, cal, ref, myTimes["Stations"]["Ida"], myTimes["Stations"]["Volta"], d, myTimes[ref][d]["Ida"], durations[0], True)
            else:
                create_json(myRoutes, cal, ref, myTimes["Stations"]["Ida"], myTimes["Stations"]["Volta"], d, myTimes[ref][d]["Ida"], durations[0])
            if d == u"Mo-Fr" and len(myTimes[ref]["Ex"]["Volta"]) > 0:
                create_json(myRoutes, cal, ref, myTimes["Stations"]["Volta"], myTimes["Stations"]["Ida"], d, myTimes[ref][d]["Volta"], durations[1], True)
            else:
                create_json(myRoutes, cal, ref, myTimes["Stations"]["Volta"], myTimes["Stations"]["Ida"], d, myTimes[ref][d]["Volta"], durations[1])
    if len(myObs) > 0:
        try:
            obs = myRoutes["routes"][ref]["observations"]
        except:
            myRoutes["routes"][ref] = {}
            myRoutes["routes"][ref]["observations"] = []
        for o in myObs:
            myRoutes["routes"][ref]["observations"].append(o)

newBlacklist = uniq(myRoutes["blacklist"])
newBlacklist.sort()
myRoutes["blacklist"] = newBlacklist
logger.info("Complete blacklist: %s", ", ".join(newBlacklist))

with open('times.json', 'w') as outfile:
    json.dump(myRoutes, outfile, sort_keys=True, indent=4)





