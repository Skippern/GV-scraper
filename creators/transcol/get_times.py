#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to download time tables as PDF and calculate route durations based on relations for the routes in OpenStreetMap
from common import *
#from feriados import *

import os
import sys
import io
import logging
import requests
import json
import datetime
import time
from unidecode import unidecode
import overpass


logger = logging.getLogger("GTFS_get_times")
logging.basicConfig(filename="/var/log/GTFS/transcol.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

cal = EspiritoSanto()

# PDFs are stored here
baseurl = "https://ceturb.es.gov.br/"

debugMe = True

# List of route numbers

config = {}
with open('transcol.json', 'r') as infile:
    config = json.load(infile)

durationsList = {}
try:
    with open('durations.json', 'r') as infile:
        durationsList = json.load(infile)
except:
    pass
myRoutes = {}
myRoutes[u"updated"] = str(datetime.date.today())
myRoutes[u"operator"] = u"Transcol"
myRoutes[u"network"] = u"Transcol"
myRoutes[u"source"] = baseurl
myRoutes[u"excluded_lines"] = []
myRoutes[u"routes"] = {}
myRoutes[u"observations"] = {}

def getTimes(ref):
    downloadURL = "https://sistemas.es.gov.br/webservices/ceturb/onibus/api/BuscaHorarios/" + ref
    myJSON = None
    myReturn = {}
    myReturn[u"Stations"] = {}
    if ref == u"521":
        myReturn[u"Stations"][u"Ida"] = u"Hotel Canto Sol"
        myReturn[u"Stations"][u"Volta"] = u"Terminal Carapina"
    elif ref == u"544":
        myReturn[u"Stations"][u"Ida"] = u"Hotel Canto Sol"
        myReturn[u"Stations"][u"Volta"] = u"Terminal Laranjeiras"
    elif ref == u"550":
        myReturn[u"Stations"][u"Ida"] = u"Shopping Vitória"
        myReturn[u"Stations"][u"Volta"] = u"Terminal Vila Velha"
    elif ref == u"842":
        myReturn[u"Stations"][u"Ida"] = u"Sesi"
        myReturn[u"Stations"][u"Volta"] = u"Terminal Laranjeuras"
    elif ref == u"867":
        myReturn[u"Stations"][u"Ida"] = u"Novo Horizonte"
        myReturn[u"Stations"][u"Volta"] = u"Terminal Carapina"
    elif ref == u"898":
        myReturn[u"Stations"][u"Ida"] = u"Terminal Laranjeiros"
        myReturn[u"Stations"][u"Volta"] = u"José de Anchieta"
    elif ref == u"899":
        myReturn[u"Stations"][u"Ida"] = u"Terminal Carapina"
        myReturn[u"Stations"][u"Volta"] = u"Castelândia"
    elif ref == u"906":
        myReturn[u"Stations"][u"Ida"] = u"Terminal Campo Grande"
        myReturn[u"Stations"][u"Volta"] = u"Soteco"
    elif ref == u"914":
        myReturn[u"Stations"][u"Ida"] = u"Terminal Campo Grande"
        myReturn[u"Stations"][u"Volta"] = u"Vila Bethânia"
    elif ref == u"916":
        myReturn[u"Stations"][u"Ida"] = u"Terminal Campo Grande"
        myReturn[u"Stations"][u"Volta"] = u"Arlindo Vilaschi"
    elif ref == u"917":
        myReturn[u"Stations"][u"Ida"] = u"Terminal Campo Grande"
        myReturn[u"Stations"][u"Volta"] = u"Areinha"
    elif ref == u"927":
        myReturn[u"Stations"][u"Ida"] = u"Terminal São Torquato"
        myReturn[u"Stations"][u"Volta"] = u"Viana"
    myReturn[ref] = {}
    myReturn[ref][u"Mo-Fr"] = {}
    myReturn[ref][u"Sa"] = {}
    myReturn[ref][u"Su"] = {}
    myReturn[ref][u"Ex"] = {}
    for rr in myReturn[ref]:
        myReturn[ref][rr][u"Ida"] = []
        myReturn[ref][rr][u"Volta"] = []
#        myReturn[ref][rr]["Circular"] = []
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
        if len(i[u"Tipo_Orientacao"]):
            nuRef = ref + i[u"Tipo_Orientacao"]
            nuRef = nuRef.strip()
            try:
                test = myReturn[nuRef]
            except:
                myReturn[nuRef] = {}
                myReturn[nuRef][u"Mo-Fr"] = {}
                myReturn[nuRef][u"Sa"] = {}
                myReturn[nuRef][u"Su"] = {}
                myReturn[nuRef][u"Ex"] = {}
                for rr in myReturn[nuRef]:
                    myReturn[nuRef][rr][u"Ida"] = []
                    myReturn[nuRef][rr][u"Volta"] = []
#                    myReturn[nuRef][rr]["Circular"] = []
        else:
            nuRef = ref
        day = None
        if i[u"TP_Horario"] == 1:
            day = u"Mo-Fr"
        elif i[u"TP_Horario"] == 2:
            day = u"Sa"
        elif i[u"TP_Horario"] == 3:
            day = u"Su"
        elif i[u"TP_Horario"] == 4:
            day = u"Ex"
        else:
            debug_to_screen( unicode(i[u"Descricao_Hora"]) )
        direction = None
        if i[u"Terminal_Seq"] == 2:
            direction = u"Ida"
        elif i[u"Terminal_Seq"] == 1:
            direction = u"Volta"
        myReturn[nuRef][day][direction].append(i[u"Hora_Saida"])
        myReturn["Stations"][direction] = lower_capitalized(i[u"Desc_Terminal"])
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
        debug_to_screen( u"{0} - {1}".format(unicode(i[u"Tipo_Orientacao"]), unicode(i[u"Descricao_Orientacao"])) )
        myObs.append( [ i[u"Tipo_Orientacao"], i[u"Descricao_Orientacao"] ] )
    return myObs

for i in getLines():
    #    if i[0] == 511 or i[0] == "511" or i[0] == u"511":
    #    break
    myRefs = []
    myTimes = {}
    ref = str(i[0])
    myRefs.append(ref)
    name = i[1]
    print ref, name
    logger.debug(u"Gathering times for route %s: %s", ref, name)
    myTimes = getTimes(ref)
    myObs = getObservations(ref)
    for j in myObs:
        tmp = ref + j[0]
        myRefs.append(tmp)
    try:
        test = myTimes[u"Stations"][u"Ida"]
    except:
        try:
            myTimes[u"Stations"][u"Ida"] = myTimes[u"Stations"][u"Volta"]
        except:
            myTimes[u"Stations"][u"Ida"], myTimes[u"Stations"][u"Volta"] = u"Unknown", u"Unknown"
    for ref in myRefs:
        try:
            durations = durationsList[ref]
        except:
            durations = [ -10, -10 ]
        if durations[0] < 0 and durations[1] < 0:
            myRoutes[u"excluded_lines"].append(ref)
            logger.info(u"%s added to Blacklist", ref)
            ref = myRefs[0]
        myDays = [ u"Mo-Fr", u"Sa", u"Su", u"Ex" ]
        for d in myDays:
            if d == u"Mo-Fr" and len(myTimes[ref][u"Ex"][u"Ida"]) > 0:
                myRoutes = create_json(myRoutes, cal, ref, myTimes[u"Stations"][u"Ida"], myTimes[u"Stations"][u"Volta"], d, myTimes[ref][d][u"Ida"], durations[0], True)
            else:
                myRoutes = create_json(myRoutes, cal, ref, myTimes[u"Stations"][u"Ida"], myTimes[u"Stations"][u"Volta"], d, myTimes[ref][d][u"Ida"], durations[0])
            if d == u"Mo-Fr" and len(myTimes[ref][u"Ex"][u"Volta"]) > 0:
                myRoutes = create_json(myRoutes, cal, ref, myTimes[u"Stations"][u"Volta"], myTimes[u"Stations"][u"Ida"], d, myTimes[ref][d][u"Volta"], durations[1], True)
            else:
                myRoutes = create_json(myRoutes, cal, ref, myTimes[u"Stations"][u"Volta"], myTimes[u"Stations"][u"Ida"], d, myTimes[ref][d][u"Volta"], durations[1])

    if len(myObs) > 0:
        try:
            obs = myRoutes[u"observations"][ref]
        except:
            myRoutes[u"observations"][ref] = []
        for o in myObs:
            myRoutes[u"observations"][ref].append(o)
            logger.debug("Observation: %s - %s", o[0], o[1])

newBlacklist = uniq(myRoutes[u"excluded_lines"])
newBlacklist.sort()
myRoutes[u"excluded_lines"] = newBlacklist
logger.info(u"Complete blacklist: %s", ", ".join(newBlacklist))

with open('times.json', 'w') as outfile:
    json.dump(myRoutes, outfile, sort_keys=True, indent=4)


