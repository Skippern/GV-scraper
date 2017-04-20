#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to download time tables as PDF and calculate route durations based on relations for the routes in OpenStreetMap

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
logging.basicConfig(filename="./GTFS_get_times.log", level=logging.WARNING, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

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
            r = requests.get(downloadURL)
        except requests.exceptions.ReadTimeout as e:
            r = False
        except requests.exceptions.ConnectionError as e:
            r = False
        try:
            myJSON = json.dumps(json.loads(r.content))
        except:
            print "r is not JSON"
    for i in json.loads(myJSON):
        routes.append( [ str(int(i[u"Linha"])), lower_capitalized(unicode(i[u"Descricao"])) ] )
    return routes

def getRefs(ref):
    stationList[ref] = {}
    
    downloadURL = "https://sistemas.es.gov.br/webservices/ceturb/onibus/api/BuscaHorarios/" + ref
    myJSON = None
    retValue = []
    r = False
    while r == False:
        try:
            r = requests.get(downloadURL)
        except requests.exceptions.ReadTimeout as e:
            r = False
        except requests.exceptions.ConnectionError as e:
            r = False
        try:
            myJSON = json.dumps(json.loads(r.content))
        except:
            print "r is not JSON"
    for i in json.loads(myJSON):
        nuRef = None
        if i["Terminal_Seq"] == 1:
            stationList[ref]["Ida"] = lower_capitalized(i["Desc_Terminal"])
        elif i["Terminal_Seq"] == 2:
            stationList[ref]["Volta"] = lower_capitalized(i["Desc_Terminal"])
        if len(i["Tipo_Orientacao"]):
            tmp = ref + i["Tipo_Orientacao"]
            retValue.append(tmp)
        retValue = uniq(retValue)
        return retValue

def uniq(values):
    output = []
    seen = set()
    for value in values:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

def lower_capitalized(input):
    newString = input.lower().replace(u"/", u" / ").replace(u".", u". ").replace(u"-", u" - ")
    toOutput = []
    for s in newString.split(u" "):
        tmp = s.capitalize()
        toOutput.append(tmp)
    newString = u" ".join(toOutput)
    output = newString.replace(u" Da ", u" da ").replace(u" Das ", u" das ").replace(u" De ", u" de ").replace(u" Do ", u" do ").replace(u" Dos ", u" dos ").replace(u" E ", u" e ").replace(u" X ", u" x ").replace(u"Via", u"via").replace(u"  ", u" ").replace(u"  ", u" ").replace(u"  ", u" ")
    # Specific place names
    output = output.replace(u"Br101", u"BR-101")
    output = output.replace(u"Br 101", u"BR-101")
    output = output.replace(u"Br 262", u"BR-262")
    output = output.replace(u"Es 010", u"ES-010")
    output = output.replace(u"Exp.", u"Expedito")
    output = output.replace(u"Expd.", u"Expedito")
    output = output.replace(u"Beira M", u"Beira Mar")
    output = output.replace(u"B. Mar", u"Beira Mar")
    output = output.replace(u"S. Dourada", u"Serra Dourada")
    output = output.replace(u"Iii", u"III")
    output = output.replace(u"Ii", u"II")
    output = output.replace(u"Jacaraipe", u"Jacaraípe")
    output = output.replace(u"Rodoviaria", u"Rodoviária")
    output = output.replace(u"P. Costa", u"Praia da Costa")
    output = output.replace(u"J. Camburi", u"Jardim Camburi")
    output = output.replace(u"M. Noronha", u"Marcilio de Noronha")
    output = output.replace(u"C. Itaperica", u"Condominio Itaparica")
    output = output.replace(u"P. Itapoã", u"Praia de Itapoã")
    output = output.replace(u"T . ", u"T. ")
    output = output.replace(u"T.", u"Terminal")
    output = output.replace(u"Itaciba", u"Utacibá")
    output = output.replace(u"Jacaraipe", u"Jacaraípe")
    output = output.replace(u"Pç", u"Praça")
    output = output.replace(u"Av.", u"Avenida")
    output = output.replace(u"Av ", u"Avenida ")
    output = output.replace(u"Torquatro", u"Torquato")
    output = output.replace(u"S. Torquato", u"São Torquato")
    output = output.replace(u"Darlysantos", u"Darly Santos")
    output = output.replace(u"Col. Laranjeiras", u"Colina de Laranjeiras")
    output = output.replace(u"B. República", u"Bairro República")
    output = output.replace(u"B. Ipanema", u"Bairro Ipanema")
    output = output.replace(u"B. Primavera", u"Bairro Primavera")
    output = output.replace(u"V. Bethânia", u"Vila Bethânia")
    output = output.replace(u"Norte/sul", u"Norte Sul")
    output = output.replace(u"Norte-sul", u"Norte Sul")
    output = output.replace(u"J. Penha", u"Jardim da Penha")
    output = output.replace(u"J. América", u"Jardim América")
    output = output.replace(u"J. America", u"Jardim América")
    output = output.replace(u"J. Marilândia", u"Jardim Marilândia")
    output = output.replace(u"Rod.", u"Rodovia")
    output = output.replace(u"Res.", u"Residencial")
    output = output.replace(u"Cdp", u"CDP")
    output = output.replace(u"Crefes", u"CREFES")
    output = output.replace(u"Ceasa", u"CEASA")
    output = output.replace(u"Ifes", u"IFES")
    output = output.replace(u"Civit", u"CIVIT")
    output = output.replace(u"V. N.", u"Vila Nova")
    output = output.replace(u"Psme", u"PSME")
    output = output.replace(u"Bl.", u"Balneário")
    output = output.replace(u"B - C - A", u"B-C-A")
    output = output.replace(u"(expresso)", u"- Expresso")
    return output.strip()

if len(sys.argv) > 1:
    sys.argv.pop(0)
    routes = sys.argv
    for i in routes:
        getRefs(i)
else:
    for i in getLines():
        for j in getRefs(i):
            routes.append(j)
    routes.sort()



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
durationsList[u"network"] = u"Seletivo"
durationsList[u"source"] = baseurl

def debug_to_screen(text, newLine=True):
    if debugMe:
        if newLine:
            print text
        else:
            print text,


def get_duration(ref, origin, destination):
    duration = 0
    points = []
    # Overpass get relation
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
                    r = requests.get(fullRoutingString)
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
                r = requests.get(searchString)
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

for i in routes:
    name = ""
    ref = i
    refA = ""
    refB = ""
    via = ""
    origin = ""
    destination = ""
    searchString = u"relation[\"type\"=\"route\"][\"ref\"=\"{0}\"][\"from\"]({1},{2},{3},{4});<<;out body;".format(unicode(ref), unicode(config["query"]["bbox"]["s"]), unicode(config["query"]["bbox"]["w"]), unicode(config["query"]["bbox"]["n"]), unicode(config["query"]["bbox"]["e"])).encode('ascii', 'replace').replace(u"?", u".")
#    searchString = u"relation[\"type\"=\"route_master\"][\"ref\"=\"{0}\"][\"operator\"=\"Transcol\"];<<;>>;out body;".format(unicode(ref), unicode(config["query"]["bbox"]["s"]), unicode(config["query"]["bbox"]["w"]), unicode(config["query"]["bbox"]["n"]), unicode(config["query"]["bbox"]["e"])).encode('ascii', 'replace').replace(u"?", u".")
#    searchString = u"relation[\"type\"=\"route\"][\"ref\"=\"{0}\"][\"from\"=\"{1}\"][\"to\"=\"{2}\";<<;>>;out body;".format(unicode(ref), unicode(config["query"]["bbox"]["s"]), unicode(config["query"]["bbox"]["w"]), unicode(config["query"]["bbox"]["n"]), unicode(config["query"]["bbox"]["e"])).encode('ascii', 'replace').replace(u"?", u".")
    logger.debug(searchString)
    api = overpass.API()
    result = False
    while result == False:
        try:
            result = api.Get(searchString, responseformat="json")
            if len(result["elements"]) < 1:
                searchString = u"relation[\"type\"=\"route\"][\"ref\"=\"{0}\"]({1},{2},{3},{4});<<;out body;".format(unicode(ref), unicode(config["query"]["bbox"]["s"]), unicode(config["query"]["bbox"]["w"]), unicode(config["query"]["bbox"]["n"]), unicode(config["query"]["bbox"]["e"])).encode('ascii', 'replace').replace(u"?", u".")
                logger.debug(searchString)
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
    if len(result["elements"]) < 1:
        continue
    for rels in result["elements"]:
        if rels["type"] == u"relation" and rels["tags"]["type"] == "route":
                refA = unicode(rels["tags"]["ref"])
#                else:
#                    refB = unicode(rels["tags"]["ref"])
            else:
                try:
                    origin = unicode(rels["tags"]["to"])
                except:
                    logger.error("Relation %s: Missing \"to\" in (%s)%s", unidecode(unicode(str(rels["id"]))), unidecode(unicode(rels["tags"]["ref"])), unidecode(unicode(rels["tags"]["name"])))
                    print "    Investigate Route \"{0}\", no \"to\" tag found".format(unidecode(unicode(rels["tags"]["ref"])))
                try:
                    destination = unicode(rels["tags"]["from"])
                except:
                    logger.error("Relation %s: Missing \"from\" in (%s)%s", unidecode(unicode(str(rels["id"]))), unidecode(unicode(rels["tags"]["ref"])), unidecode(unicode(rels["tags"]["name"])))
                    print "    Investigate Route \"{0}\", no \"from\" tag found".format(unidecode(unicode(rels["tags"]["ref"])))
#                if ref != unicode(rels["tags"]["ref"]):
                refB = unicode(rels["tags"]["ref"])
            if origin == destination:
                logger.error("Relation %s: Same origin and destination: %s", unidecode(unicode(str(rels["id"]))), unidecode(unicode(origin)))
                print "    Investigate Route \"{0}\", same \"from\" and \"to\" values: {1}".format(unidecode(unicode(str(rels["id"]))), unidecode(unicode(origin)))
    print ref, name
    print "    From:", origin
    print "    To:", destination
    if via != "":
        print "    Via:", ", ".join(via.split(";"))
    print "    Variations:",
    if refA != ref and refA != "" and refA != u"":
        print refA,
    if refB != ref and refB != "" and refB != u"":
        print refB,
    print " "
    durationsList[ref] = [ get_duration(ref, origin, destination), get_duration(ref, destination, origin) ]
    print "Durations calculated ",ref, ":", durationsList[ref]
    if refA != ref and refA != "" and refA != u"":
        durationsList[refA] = [ get_duration(refA, origin, destination), get_duration(refA, destination, origin) ]
        print "Durations calculated ",refA, ":", durationsList[refA]
    if refB != ref and refB != "" and refB != u"":
        durationsList[refB] = [ get_duration(refB, origin, destination), get_duration(refB, destination, origin) ]
        print "Durations calculated ",refB, ":", durationsList[refB]

with open('durations.json', 'w') as outfile:
    json.dump(durationsList, outfile, sort_keys=True, indent=4)






