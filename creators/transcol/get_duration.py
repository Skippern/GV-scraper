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
from unidecode import unidecode
routingE = "YOURS"
try:
    import osrm
    routingE = "OSRM"
except:
    pass
import overpass


logger = logging.getLogger("GTFS_get_durations")
logging.basicConfig(filename="./GTFS_get_times.log", level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

# PDFs are stored here
baseurl = "http://ceturb.es.gov.br/"

debugMe = False

# List of route numbers
routes = [  ]
stationList = {}

def getLines():
    downloadURL = "https://sistemas.es.gov.br/webservices/ceturb/onibus/api/ConsultaLinha/"
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
            print "r is not JSON"
            r = False
    for i in json.loads(myJSON):
        routes.append( [ str(int(i[u"Linha"])), lower_capitalized(unicode(i[u"Descricao"])) ] )
    logger.debug("%s lines gathered from site", len(routes))
    return routes

def getRefs(ref):
    ref = ref.strip()
    #    print "Testing getRefs on", ref
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
            print "r is not JSON"
            r = False
    for i in json.loads(myJSON):
        if i["Terminal_Seq"] == 1:
            stationList[ref][0] = lower_capitalized(i["Desc_Terminal"])
        elif i["Terminal_Seq"] == 2:
            stationList[ref][1] = lower_capitalized(i["Desc_Terminal"])
        else:
            print i["Terminal_Seq"], i["Desc_Terminal"]
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
            routes.append(j)
    routes.sort()
    logger.info("Full route list to execute: %s", ", ".join(routes))
else:
    logger.info("Executing default list from %s", baseurl)
    for i in getLines():
        print "Getting variations for", i[0], "-", i[1]
        for j in getRefs(i[0]):
            routes.append(j)
    routes.sort()
    logger.info("Full route list to execute: %s", ", ".join(routes))
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

def debug_to_screen(text, newLine=True):
    if debugMe:
        if newLine:
            print text
        else:
            print text,


def get_duration(ref, origin, destination):
    if origin == None:
        return -9
    duration = 0
    points = []
    # Overpass get relation
    if destination == None:
        searchString = u"relation[\"type\"=\"route\"][\"route\"=\"bus\"][\"ref\"=\"{0}\"][\"from\"~\"{1}\"]({3},{4},{5},{6});out body;>;".format(unicode(ref), unicode(origin), unicode(destination), unicode(config["query"]["bbox"]["s"]), unicode(config["query"]["bbox"]["w"]), unicode(config["query"]["bbox"]["n"]), unicode(config["query"]["bbox"]["e"])).encode('ascii', 'replace').replace(u"?", u".")
    else:
        searchString = u"relation[\"type\"=\"route\"][\"route\"=\"bus\"][\"ref\"=\"{0}\"][\"from\"~\"{1}\"][\"to\"~\"{2}\"]({3},{4},{5},{6});out body;>;".format(unicode(ref), unicode(origin), unicode(destination), unicode(config["query"]["bbox"]["s"]), unicode(config["query"]["bbox"]["w"]), unicode(config["query"]["bbox"]["n"]), unicode(config["query"]["bbox"]["e"])).encode('ascii', 'replace').replace(u"?", u".")
    logger.debug(searchString)
    api = overpass.API()
    result = False
    while result == False:
        try:
            result = api.Get(searchString, responseformat="json")
        except overpass.errors.OverpassSyntaxError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: %s", e)
            continue
        except overpass.errors.UnknownOverpassError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: %s", e)
            continue
        except overpass.errors.TimeoutError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: %s", e)
            continue
        except overpass.errors.ServerRuntimeError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: %s", e)
            continue
        except overpass.errors.MultipleRequestsError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: %s", e)
            continue
        except overpass.errors.ServerLoadError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: %s", e)
            continue
        except requests.exceptions.ConnectionError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: %s", e)
            continue
        try:
            json.loads(json.dumps(result))
        except TypeError as e:
            result = False
            logger.debug("Retrieved data was not JSON readable, sleeping for 120s and trying again: %s", e)
            time.sleep(120)
        except ValueError as e:
            result = False
            logger.debug("Retrieved data was not JSON readable, sleeping for 120s and trying again: %s", e)
            time.sleep(120)
    nodeList = []
    # Make points list
    if len(result["elements"]) < 1:
        logger.error("No relation found: \"%s\" from %s to %s", unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
        print "    Investigate route \"{0}\" from {1} to {2}. Relation not found".format(unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
        duration = -5
        return duration
    for elm in result["elements"]:
        if elm["type"] == u"relation":
            if elm["members"][0]["role"] != u"stop":
                logger.error("Route \"%s\" from %s to %s doesn't start with a stop", unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
                print "    Investigate route \"{0}\" from {1} to {2}. Route doesn't start with a stop".format(unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
                return -3
            if elm["members"][-1]["role"] != u"stop":
                logger.error("Route \"%s\" from %s to %s doesn't end with a stop", unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
                print "    Investigate route \"{0}\" from {1} to {2}. Route doesn't end with a stop".format(unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
                return -4
            for m in elm["members"]:
                if m["role"] == u"stop" and m["type"] == u"node":
                    nodeList.append(m["ref"])
    for testNode in nodeList:
        for elm in result["elements"]:
            if elm["type"] == u"node" and elm["id"] == testNode:
                points.append( ( elm["lat"], elm["lon"] ) )
    if len(points) == 0:
        logger.error("Relation have no defined stops: \"%s\" from %s to %s", unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
        print "    Investigate route \"{0}\" from {1} to {2}. Relation have no stops mapped".format(unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
        duration = -1
        return duration
    elif len(points) == 1:
        logger.error("Relation have only one defined stop: \"%s\" from %s to %s", unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
        print "    Investigate route \"{0}\" from {1} to {2}. Relation have only one defined stop".format(unidecode(unicode(ref)), unidecode(unicode(origin)), unidecode(unicode(destination)))
        duration = -2
        return duration
#    print "Routing with {0} nodes!".format(len(points))
    # Get Route
    if routingE == "OSRM":
        result = osrm.match(points, steps=False, overview="full")
        tmp = result["total_time"]
        duration = int(float(tmp)/60.0) + 1
    elif routingE == "YOURS":
        routingBase = "http://www.yournavigation.org/api/1.0/gosmore.php?format=json&v=psv&fast=1&"
        fromP = None
        for p in points:
            toP = p
            if fromP == None:
                fromP = toP
            else:
                r = False
                while r == False:
                    fullRoutingString = "{0}&flat={1}&flon={2}&tlat={3}&tlon={4}".format(routingBase,fromP[0],fromP[1],toP[0],toP[1])
                    try:
                        r = requests.get(fullRoutingString, timeout=30)
                    except requests.exceptions.ConnectionError as e:
                        r = False
                    except requests.exceptions.ReadTimeout as e:
                        r = False
                getDuration = r.content
                try:
                    duration += int(getDuration[(getDuration.find("<traveltime>")+12):getDuration.find("</traveltime>")])
                except:
                    r = False
            fromP = toP
        duration = int( float(duration) / 60.0 ) + int( float(len(points) * 10) / 60.0 ) + 1
    else:
        searchString = "http://router.project-osrm.org/route/v1/driving/"
        for p in points:
            searchString = "{0}{1},{2};".format(searchString,p[0],p[1])
        searchString = "{0}?{1}".format(searchString[:-1],"overview=false")
        r = False
        myRoute = {}
        while r == False:
            try:
                r = requests.get(searchString, timeout=30)
            except requests.exceptions.ReadTimeout as e:
                r = False
            except requests.exceptions.ConnectionError as e:
                r = False
            try:
                myRoute = json.loads(r.content)
            except:
                r = False
                time.sleep(10)
        for x in myRoute["routes"]:
            duration += x["duration"]
        duration = int(float(duration)/60.0)+1
    # Return
    return duration

#print routes
for i in routes:
    if len(i) > 3:
        ref = i[:3]
    else:
        ref = i
    #    print ref
    origin = stationList[ref][0]
    destination = stationList[ref][1]
    print "    Route:", i
    print "    From:", origin
    print "    To:", destination
    durationsList[i] = [ get_duration(i, origin, destination), get_duration(i, destination, origin) ]
    print "Durations calculated ",i, ":", durationsList[i]

with open('durations.json', 'w') as outfile:
    json.dump(durationsList, outfile, sort_keys=True, indent=4)






