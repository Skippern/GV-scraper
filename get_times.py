#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to download time tables as PDF and extract times into containers that can be used by OSM2GFTS
#  or similar

import os
import sys
import io
import logging
import requests
import json
import datetime
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTRect
from pdfminer.converter import PDFPageAggregator

logger = logging.getLogger("GFTS_get_times")
logging.basicConfig(filename="./GFTS_get_times.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

# PDFs are stored here
baseurl = "http://www.expressolorenzutti.com.br/horarios/"

# List of route numbers
routes = [ "001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013", "014", "015", "016", "017", "018", "019", "020", "021", "022", "023", "024", "025", "026", "027", "028", "029", "030", "031", "032", "033", "034", "035", "036", "037", "038", "039", "040", "041", "042", "043", "044", "045", "046", "047", "048", "049", "050", "051", "052", "053", "054", "055", "056", "057", "058" ]
#routes = [ "001", "009" ]
myRoutes = {}

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
            return None
    else:
        return None

def create_json(fromV, toV, weekdays, saturdays, sundays):
    retValue = {}
    retValue[u"from"] = fromV
    retValue[u"to"] = toV
    retValue[u"WD"] = weekdays
    retValue[u"Sa"] = saturdays
    retValue[u"Su"] = sundays
    return retValue

myRoutes[u"updated"] = str(datetime.date.today())
myRoutes[u"operator"] = u"Expresso Lorenzutti"
myRoutes[u"network"] = u"PMG"
myRoutes[u"source"] = baseurl
myRoutes[u"routes"] = {}

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
        wd_ida = []
        wd_volta = []
        sa_ida = []
        sa_volta = []
        su_ida = []
        su_volta = []
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
                    tmpList.pop(0)
                    tmpList.pop(0)
                    name = u" ".join(tmpList).strip()
                    fieldNr += 1
                elif fieldNr == 2:
                    origin = object.get_text().strip()
                    fieldNr += 1
                elif fieldNr == 4:
                    destination = object.get_text().strip()
                    fieldNr += 1
                else:
                    tmp = object.get_text()
                    # Try to split tmp at linebreaks for fields with multiple times
                    tmpList = tmp.split(u"\n")
                    for t in tmpList:
                        t = t.strip()
                        for x in t.split():
                            if x[0] == u"0" or x[0] == u"1" or x[0] == u"2":
                                if len(t) > 10:
                                    continue
                                dir = "ida"
                                if object.bbox[0] > 225.0:
                                    dir = "volta"
                                dayOfWeek = "sa"
                                if object.bbox[1] < 236.0:
                                    dayOfWeek = "su"
                                elif object.bbox[1] > 415.0:
                                    dayOfWeek = "wd"
                                if dir == "ida" and dayOfWeek == "wd":
                                    wd_ida.append(t)
                                elif dir == "volta" and dayOfWeek == "wd":
                                    wd_volta.append(t)
                                elif dir == "ida" and dayOfWeek == "sa":
                                    sa_ida.append(t)
                                elif dir == "volta" and dayOfWeek == "sa":
                                    sa_volta.append(t)
                                elif dir == "ida" and dayOfWeek == "su":
                                    su_ida.append(t)
                                elif dir == "volta" and dayOfWeek == "su":
                                    su_volta.append(t)
#                                print t, object.bbox
                            else:
                                continue
        name = name.split(u"\n")[0]
        print ref, name
        print "    From", origin
        print "    To", destination
        myRoutes["routes"][ref] = [ create_json(origin, destination, wd_ida, sa_ida, su_ida),
                                   create_json(destination, origin, wd_volta, sa_volta, su_volta) ]
with open('timetable.json', 'w') as outfile:
    json.dump(myRoutes, outfile, sort_keys=True, indent=4)






