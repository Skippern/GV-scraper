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
logging.basicConfig(filename="./GTFS_get_times.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

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
myRoutes["routes"] = {}

def calculate_end_time(start_time, duration):
    if duration < 1:
        duration = 60
    end_time = start_time
    day = 0
    hr = int(start_time[:2])
    min = int(start_time[3:])
    min += duration
    while min > 59:
        hr += 1
        min -= 60
    while hr > 23:
        hr -= 24 # Should we put a day+1 variable as well?
        day += 1
    end_time = "{0}:{1}".format(str(hr).zfill(2), str(min).zfill(2))
    if day > 0:
        end_time = "{0}+{1}".format(end_time, str(day))
    return end_time

def getLines():
    downloadURL = "https://sistemas.es.gov.br/webservices/ceturb/onibus/api/ConsultaLinha?Tipo_Linha=Seletivo"
    routes = []
    myJSON = None
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
        routes.append( [ str(int(i[u"Linha"])), lower_capitalized(unicode(i[u"Descricao"])) ] )
    return routes

def getTimes(ref):
    downloadURL = "https://sistemas.es.gov.br/webservices/ceturb/onibus/api/BuscaHorarios/" + ref
    myJSON = None
    myReturn = {}
    myReturn["Stations"] = {}
    myReturn[ref] = {}
    myReturn[ref]["Mo-Fr"] = {}
    myReturn[ref]["Sa"] = {}
    myReturn[ref]["Su"] = {}
    myReturn[ref]["Ex"] = {}
    for rr in myReturn[ref]:
        myReturn[ref][rr]["Ida"] = []
        myReturn[ref][rr]["Volta"] = []
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
#                    myReturn[nuRef][rr]["Circular"] = []
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
        if i["Terminal_Seq"] == 1:
            direction = "Ida"
        elif i["Terminal_Seq"] == 2:
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

def create_json(ref, fromV, toV, d, times, duration=60, atypical=False):
    debug_to_screen(u"{0} - {1} -> {2} ({3}) {4} - {5}".format(ref, fromV, toV, d, len(times), duration))
    times.sort()
    retValue = {}
    retValue[u"from"] = fromV
    retValue[u"to"] = toV
    if d == "Su":
        retValue[u"service"] = [ d ]
        tmp = [ d ]
        for i in get_saturday_holidays():
            tmp.append(i)
        for i in get_weekday_holidays():
            tmp.append(i)
        retValue[u"service"] = [ tmp ]
        retValue[u"exceptions"] = []
    elif d == "Sa":
        retValue[u"service"] = [ d ]
        retValue[u"exceptions"] = [ get_saturday_holidays() ]
    elif d == "Ex":
        retValue[u"service"] = [ get_atypical_days() ]
        retValue[u"exceptions"] = []
    else:
        retValue[u"service"] = [ d ]
        if atypical == True:
            tmp = get_weekday_holidays()
            for i in get_atypical_days():
                tmp.append(i)
            retValue[u"exceptions"] = [ tmp ]
        else:
            retValue[u"exceptions"] = [ get_weekday_holidays() ]
    retValue[u"stations"] = [ fromV, toV ]
    retValue[u"times"] = []
    for t in times:
        tmp = calculate_end_time(t, duration)
        retValue[u"times"].append( [ t, tmp ] )
    if len(retValue["times"]) > 0:
        try:
            test = myRoutes["routes"][ref]
        except:
            myRoutes["routes"][ref] = []
        myRoutes["routes"][ref].append(retValue)

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
        myDays = [ u"Mo-Fr", u"Sa", u"Su", u"Ex" ]
        for d in myDays:
            if d == u"Mo-Fr" and len(myTimes[ref]["Ex"]["Ida"]) > 0:
                create_json(ref, myTimes["Stations"]["Ida"], myTimes["Stations"]["Volta"], d, myTimes[ref][d]["Ida"], durations[0], True)
            else:
                create_json(ref, myTimes["Stations"]["Ida"], myTimes["Stations"]["Volta"], d, myTimes[ref][d]["Ida"], durations[0])
            if d == u"Mo-Fr" and len(myTimes[ref]["Ex"]["Volta"]) > 0:
                create_json(ref, myTimes["Stations"]["Volta"], myTimes["Stations"]["Ida"], d, myTimes[ref][d]["Volta"], durations[1], True)
            else:
                create_json(ref, myTimes["Stations"]["Volta"], myTimes["Stations"]["Ida"], d, myTimes[ref][d]["Volta"], durations[1])
    if len(myObs) > 0:
        try:
            obs = myRoutes["routes"][ref]["observations"]
        except:
            myRoutes["routes"][ref] = {}
            myRoutes["routes"][ref]["observations"] = []
        for o in myObs:
            myRoutes["routes"][ref]["observations"].append(o)

with open('times.json', 'w') as outfile:
    json.dump(myRoutes, outfile, sort_keys=True, indent=4)






