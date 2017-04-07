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
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTRect
from pdfminer.converter import PDFPageAggregator
routingE = "YOURS"
try:
    import osrm
    routingE = "OSRM"
except:
    pass
import overpass


logger = logging.getLogger("GTFS_get_durations")
logging.basicConfig(filename="./GTFS_get_times.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

# PDFs are stored here
baseurl = "http://www.expressolorenzutti.com.br/horarios/"

debugMe = False

# List of route numbers
routes = [ "001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013", "014", "015", "016", "017", "018", "019", "020", "021", "022", "023", "024", "025", "026", "027", "028", "029", "030", "031", "032", "033", "034", "035", "036", "037", "038", "039", "040", "041", "042", "043", "044", "045", "046", "047", "048", "049", "050", "051", "052", "053", "054", "055", "056", "057", "058" ]

if len(sys.argv) > 1:
    sys.argv.pop(0)
    routes = sys.argv

config = {}
with open('lorenzutti.json', 'r') as infile:
    config = json.load(infile)

durationsList = {}
with open('durations.json', 'r') as infile:
    durationsList = json.load(infile)
durationsList[u"updated"] = str(datetime.date.today())
durationsList[u"operator"] = u"Expresso Lorenzutti"
durationsList[u"network"] = u"PMG"
durationsList[u"source"] = baseurl

def debug_to_screen(text, newLine=True):
    if debugMe:
        if newLine:
            print text
        else:
            print text,

def uniq(values):
    output = []
    seen = set()
    for value in values:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

def download_pdf(i):
    downloadURL = baseurl + i + ".pdf"
    r = False
    while r == False:
        try:
            r = requests.get(downloadURL)
        except requests.exceptions.ReadTimeout as e:
            r = False
        except requests.exceptions.ConnectionError as e:
            r = False
    if r.status_code == 200:
        if r.headers.get('content-length') > 0:
            logger.debug("Successfully downloaded %s.pdf", i)
            return r.content
        else:
            logger.debug("No file downloaded for %s, skipping", i)
            return None
    else:
        logger.debug("No file downloaded for %s, skipping", i)
        return None

def lower_capitalized(input):
    newString = input.lower().replace(u"n. s .", u"nossa senhora da ").replace(u".", u". ")
    toOutput = []
    for s in newString.split(u" "):
        tmp = s.capitalize()
        toOutput.append(tmp)
    newString = u" ".join(toOutput)
    output = newString.replace(u" Da ", u" da ").replace(u" Das ", u" das ").replace(u" De ", u" de ").replace(u" Do ", u" do ").replace(u" Dos ", u" dos ").replace(u" E ", u" e ").replace(u"Sesc", u"SESC").replace(u"sesc", u"SESC").replace(u" X ", u" x ").replace(u"Ciac", u"CIAC").replace(u"Via", u"via").replace(u"Br ", u"BR-").replace(u"Br-", u"BR-").replace(u"Br1", u"BR-1").replace(u"Caic", u"CAIC").replace(u"  ", u" ")
# Specific place names
    output = output.replace(u"Trevo Setiba", u"Trevo de Setiba")
    output = output.replace(u"Trevo BR-101", u"Trevo da BR-101")
    output = output.replace(u"Santa Monica", u"Santa Mônica")
    output = output.replace(u"Pontal Santa Mônica", u"Pontal de Santa Mônica")
    output = output.replace(u"Vitoria", u"Vitória")
    output = output.replace(u"Praça Vitória", u"Praça da Vitória")
    output = output.replace(u"Ewerson de A. Sodré", u"Ewerson de Abreu Sodré")
    output = output.replace(u"Meaipe", u"Meaípe")
    output = output.replace(u"J. Boa Vista", u"Jardim Boa Vista")
    output = output.replace(u"Jabarai", u"Jabaraí")
    output = output.replace(u"olaria", u"Olaria")
    output = output.replace(u"muquiçaba", u"Muquiçaba")
    output = output.replace(u"Independencia", u"Independência")
    output = output.replace(u"Patura", u"Paturá")
    output = output.replace(u"Iguape", u"Iguapé")
    return output

def get_duration(ref, origin, destination):
    duration = 0
    points = []
    # Overpass get relation
    searchString = u"relation[\"type\"=\"route\"][\"route\"=\"bus\"][\"ref\"=\"{0}\"][\"from\"~\"{1}\"][\"to\"~\"{2}\"]({3},{4},{5},{6});out body;>;".format(unicode(ref), unicode(origin), unicode(destination), unicode(config["query"]["bbox"]["s"]), unicode(config["query"]["bbox"]["w"]), unicode(config["query"]["bbox"]["n"]), unicode(config["query"]["bbox"]["e"])).encode('ascii', 'replace').replace(u"?", u".")
    api = overpass.API()
    result = False
    while result == False:
        try:
            result = api.Get(searchString, responseformat="json")
        except overpass.errors.OverpassSyntaxError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: {0}", e)
            continue
        except overpass.errors.UnknownOverpassError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: {0}", e)
            continue
        except overpass.errors.TimeoutError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: {0}", e)
            continue
        except overpass.errors.ServerRuntimeError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: {0}", e)
            continue
        except overpass.errors.MultipleRequestsError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: {0}", e)
            continue
        except overpass.errors.ServerLoadError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: {0}", e)
            continue
        except requests.exceptions.ConnectionError as e:
            time.sleep(120)
            logger.debug("Some problems in overpass process, sleeping for 120s: {0}", e)
            continue
        try:
            json.loads(json.dumps(result))
        except TypeError as e:
            result = False
            logger.debug("Retrieved data was not JSON readable, sleeping for 120s and trying again: {0}", e)
            time.sleep(120)
        except ValueError as e:
            result = False
            logger.debug("Retrieved data was not JSON readable, sleeping for 120s and trying again: {0}", e)
            time.sleep(120)
    nodeList = []
    # Make points list
    for elm in result["elements"]:
        if elm["type"] == u"relation":
            for m in elm["members"]:
                if m["role"] == u"stop" and m["type"] == u"node":
                    nodeList.append(m["ref"])
    for testNode in nodeList:
        for elm in result["elements"]:
            if elm["type"] == u"node" and elm["id"] == testNode:
                points.append( ( elm["lat"], elm["lon"] ) )
    if len(points) == 0:
        logger.debug("No relation found, or relation have no defined stops: \"%s\" from %s to %s", ref, origin, destination)
        print "    Investigate route \"{0}\" from {1} to {2}. Relation not found, or have no stops mapped".format(ref, unidecode(origin), unidecode(destination))
        duration = -1
        return duration
    elif len(points) == 1:
        loger.debug("Relation have only one defined stop: \"%s\" from %s to %s", ref, origin, destination)
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
                duration += int(getDuration[(getDuration.find("<traveltime>")+12):getDuration.find("</traveltime>")])
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
    if abs(duration) < 1:
        duration = int( ( float(durationsList[ref][0]) + float(durationsList[ref][1]) ) / 2.0 )
        print "    !!! Values overrided"
    return duration

for i in routes:
    pdf = download_pdf(i)
    if pdf == None:
        continue
    # Start pdfminer
    parser = PDFParser(io.BytesIO(pdf))
    document = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        layout = device.get_result()
        fieldNr = 0
        ref = ""
        name = ""
        origin = ""
        destination = ""
        variationGrepper = []
        refList = []
        refSet = set()
        for object in layout:
            if not issubclass(type(object), LTRect):
                # Here we have all data objects on the page, we now need to get their values and match them with the right variables
                tmp = object.get_text().strip()
                if tmp == u"EXPRESSO LORENZUTTI" or tmp == u"ITINERARIO" or tmp == u"AOS DOMINGOS" or tmp == u"AOS SABADOS" or tmp == u"DIAS UTEIS":
                    continue
                if tmp == u"PARTIDAS:":
                    fieldNr += 1
                    continue
                tmpList = tmp.split(u" ")
                if tmpList[0] == u"Início" or tmpList[0] == u"Inicio":
                    continue
                if fieldNr == 0:
                    tmp = object.get_text()
                    tmpList = tmp.split(u" ")
                    tmpList.pop(0)
                    ref = tmpList[0]
                    refList.append(ref)
                    refSet.add(ref)
                    tmpList.pop(0)
                    tmpList.pop(0)
                    name = lower_capitalized(u" ".join(tmpList).strip())
                    fieldNr += 1
                elif fieldNr == 2:
                    origin = lower_capitalized(object.get_text().strip())
                    fieldNr += 1
                elif fieldNr == 4:
                    destination = lower_capitalized(object.get_text().strip())
                    fieldNr += 1
                else:
                    variationGrepper.append(object.get_text().strip())
            for vars in variationGrepper:
                vars = vars.strip()
                if len(vars) < 4:
                    print vars
                    tmp = u"{0} {1}".format(ref, vars).strip()
                    if tmp not in refSet:
                        refList.append(tmp)
                        refSet.add(tmp)
                if vars[0] != u"0" and vars[0] != u"1" and vars[0] != u"2":
                    continue
                if len(vars) > 10:
                    continue
                if ref not in refSet:
                    refList.append(ref)
                    refSet.add(ref)
                if len(vars) > 4:
                    print vars
                    variation = vars[5:].strip()
                    tmp = u"{0} {1}".format(ref, variation).strip()
                    if tmp not in refSet:
                        refList.append(tmp)
                        refSet.add(tmp)
        name = name.split(u"\n")[0]
        print ref, name
        print "    From", origin
        print "    To", destination
        refList = uniq(refList)
        refList.sort()
        for myRef in refList:
            durationsList[myRef] = [ get_duration(myRef, origin, destination), get_duration(myRef, destination, origin) ]
        print "Durations calculated: ", durationsList[ref]

with open('durations.json', 'w') as outfile:
    json.dump(durationsList, outfile, sort_keys=True, indent=4)






