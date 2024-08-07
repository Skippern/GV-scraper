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
import datetime
import time
#from unidecode import unidecode
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTRect
from pdfminer.converter import PDFPageAggregator
import overpass


logger = logging.getLogger("GTFS_get_durations")
logging.basicConfig(filename="/var/log/GTFS/lorenzutti.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

# PDFs are stored here
baseurl = "http://www.expressolorenzutti.com.br/horarios"

if len(sys.argv) > 1:
    sys.argv.pop(0)
    routes = sys.argv

config = {}
with open('lorenzutti.json', 'r') as infile:
    config = json.load(infile)

durationsList = {}
try:
    with open('durations.json', 'r') as infile:
        durationsList = json.load(infile)
except:
    pass
durationsList[u"updated"] = str(datetime.date.today())
durationsList[u"operator"] = u"Expresso Lorenzutti"
durationsList[u"network"] = u"PMG"
durationsList[u"source"] = baseurl

for i in getLines():
    pdf = download_pdf(i)
    if pdf == None:
        continue
    # Start pdfminer
    with open("pdf/{0}.pdf".format(i), 'w') as outfile:
        outfile.write(pdf)
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
        ref = u""
        name = u""
        origin = u""
        destination = u""
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
                    tmp = u"{0} {1}".format(ref, vars).strip()
                    if tmp not in refSet:
                        refList.append(tmp)
                        refSet.add(tmp)
                try:
                    if vars[0] != u"0" and vars[0] != u"1" and vars[0] != u"2":
                        continue
                except:
                    pass
                if len(vars) > 10:
                    continue
                if ref not in refSet:
                    refList.append(ref)
                    refSet.add(ref)
                if len(vars) > 4:
                    variation = vars[5:].strip()
                    tmp = u"{0} {1}".format(ref, variation).strip()
                    if tmp not in refSet:
                        refList.append(tmp)
                        refSet.add(tmp)
        name = name.split(u"\n")[0]
        print ref, name
        print u"    From", origin
        print u"    To", destination
        refList = uniq(refList)
        refList.sort()
        for myRef in refList:
            durationsList[myRef] = [ get_duration(myRef, origin, destination, config["query"]["bbox"]), get_duration(myRef, destination, origin, config["query"]["bbox"]) ]
        print u"Durations calculated: ", durationsList[ref]

with open('durations.json', 'w') as outfile:
    json.dump(durationsList, outfile, sort_keys=True, indent=4)






