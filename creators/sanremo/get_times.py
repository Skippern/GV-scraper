#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to download time tables as PDF and extract times into containers that can be used by OSM2GFTS
#  or similar
from common import *

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
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTRect, LTLine
from pdfminer.converter import PDFPageAggregator

logger = logging.getLogger("GTFS_get_times")
logging.basicConfig(filename="/var/log/GTFS/sanremo.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

cal = Guarapari()

# PDFs are stored here
baseurl = "http://www.viacaosanremo.com.br/horarios/"

blacklisted = [ ]
whitelisted = [ ]


ignoreVariants = True
blacklistVariants = True

myRoutes = {}

durationsList = {}
with open('durations.json', 'r') as infile:
    durationsList = json.load(infile)

def download_pdf(i):
    downloadURL = baseurl + i + ".pdf"
    r = False
    while r == False:
        try:
            r = requests.get(downloadURL, timeout=30)
        except requests.exceptions.ReadTimeout as e:
            r = False
        except requests.exceptions.ConnectionError as e:
            r = False
    if r.status_code == 200:
        if r.headers.get('content-length') > 0:
            logger.debug("Successfully downloaded %s.pdf", i)
            return r.content
        else:
            myRoutes[u"blacklist"].append(i)
            logger.error("%s added to blacklist (file does not exist or contain no data)", i)
            return None
    else:
        myRoutes[u"blacklist"].append(i)
        logger.error("%s added to blacklist (file does not exist or contain no data)", i)
        return None

myRoutes[u"updated"] = str(datetime.date.today())
myRoutes[u"operator"] = u"Viação Sanremo"
myRoutes[u"network"] = u"PMVV"
myRoutes[u"source"] = baseurl
myRoutes[u"blacklist"] = []
myRoutes[u"routes"] = {}

whitelistSet = set()

for wl in whitelisted:
    whitelistSet.add(wl)

for bl in blacklisted:
    myRoutes["blacklist"].append(bl)

for i in getLines():
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
            if not issubclass(type(object), LTRect) and not issubclass(type(object), LTLine):
                # Here we have all data objects on the page, we now need to get their values and match them with the right variables
                tmp = object.get_text().strip()
                if tmp == u"VIAÇÃO SANREMO LTDA" or tmp == u"ITINERARIO" or tmp == u"AOS DOMINGOS" or tmp == u"AOS SABADOS" or tmp == u"DIAS UTEIS" or tmp == u"OBS.:":
                    continue
                if tmp == u"PARTIDAS:":
                    fieldNr += 1
                    continue
                tmpList = tmp.split(u" ")
                if tmpList[0] == u"Início" or tmpList[0] == u"Inicio":
                    continue
                #print fieldNr, tmp
                if tmpList[0] == u"PARTIDAS:":
                    tmpList.pop(0)
                    tmp = u" ".join(tmpList)
                    fieldNr += 1
                if fieldNr == 0:
                    tmp = object.get_text()
                    tmpList = tmp.split(u" ")
                    tmpList.pop(0)
                    ref = tmpList[0]
#                    refList.append(ref)
#                    refSet.add(ref)
                    tmpList.pop(0)
                    tmpList.pop(0)
                    name = lower_capitalized(u" ".join(tmpList).strip())
                    fieldNr += 1
                elif fieldNr == 2:
                    origin = lower_capitalized(unicode(tmp))
                    fieldNr += 1
                elif fieldNr == 4:
                    destination = lower_capitalized(unicode(tmp))
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
                            else:
                                continue
        name = name.split(u"\n")[0]
        print ref, name
        print "    From", origin
        print "    To", destination
        # Here we need some code to handle variations, for now we'll just strip the information after the time stamp
        wd_ida = uniq(wd_ida)
        wd_volta = uniq(wd_volta)
        sa_ida = uniq(sa_ida)
        sa_volta = uniq(sa_volta)
        su_ida = uniq(su_ida)
        su_volta = uniq(su_volta)
        wd_ida.sort()
        wd_volta.sort()
        sa_ida.sort()
        sa_volta.sort()
        su_ida.sort()
        su_volta.sort()
        myVariations = []
        myVariationList = {}
        variationSet = set()
        myVariationList[ref] = {}
        myVariationList[ref]["ida"] = {}
        myVariationList[ref]["volta"] = {}
        myVariationList[ref]["ida"]["Mo-Fr"] = []
        myVariationList[ref]["volta"]["Mo-Fr"] = []
        myVariationList[ref]["ida"]["Sa"] = []
        myVariationList[ref]["volta"]["Sa"] = []
        myVariationList[ref]["ida"]["Su"] = []
        myVariationList[ref]["volta"]["Su"] = []
        while len(wd_ida) > 0:
            t = wd_ida[0]
            wd_ida.pop(0)
            debug_to_screen("(wi) {0}".format(t), False)
            if len(t) > 5:
                newT = t[:5]
                variation = t[5:].strip()
                debug_to_screen("(wi) Variation in \"{0}\"/\"{1}\"/\"{2}\"".format(t,newT,variation))
                if ignoreVariants:
                    if ref not in whitelistSet:
                        myVariationList[ref]["ida"]["Mo-Fr"].append(newT)
                    else:
                        debug_to_screen("Forced variation (wi)")
                myVariations.append(variation)
                tmp = u"{0} {1}".format(ref, variation)
                if variation not in variationSet:
                    variationSet.add(variation)
                    myVariationList[tmp] = {}
                    myVariationList[tmp]["ida"] = {}
                    myVariationList[tmp]["volta"] = {}
                    myVariationList[tmp]["ida"]["Mo-Fr"] = []
                    myVariationList[tmp]["volta"]["Mo-Fr"] = []
                    myVariationList[tmp]["ida"]["Sa"] = []
                    myVariationList[tmp]["volta"]["Sa"] = []
                    myVariationList[tmp]["ida"]["Su"] = []
                    myVariationList[tmp]["volta"]["Su"] = []
                myVariationList[tmp]["ida"]["Mo-Fr"].append(newT)
            else:
                debug_to_screen(len(t))
                myVariationList[ref]["ida"]["Mo-Fr"].append(t)
        while len(wd_volta) > 0:
            t = wd_volta[0]
            wd_volta.pop(0)
            debug_to_screen("(wv) {0}".format(t), False)
            if len(t) > 5:
                newT = t[:5]
                variation = t[5:].strip()
                debug_to_screen("(wv) Variation in \"{0}\"/\"{1}\"/\"{2}\"".format(t,newT,variation))
                if ignoreVariants:
                    if ref not in whitelistSet:
                        myVariationList[ref]["volta"]["Mo-Fr"].append(newT)
                    else:
                        debug_to_screen("Forced variation (wv)")
                myVariations.append(variation)
                tmp = u"{0} {1}".format(ref, variation)
                if variation not in variationSet:
                    variationSet.add(variation)
                    myVariationList[tmp] = {}
                    myVariationList[tmp]["ida"] = {}
                    myVariationList[tmp]["volta"] = {}
                    myVariationList[tmp]["ida"]["Mo-Fr"] = []
                    myVariationList[tmp]["volta"]["Mo-Fr"] = []
                    myVariationList[tmp]["ida"]["Sa"] = []
                    myVariationList[tmp]["volta"]["Sa"] = []
                    myVariationList[tmp]["ida"]["Su"] = []
                    myVariationList[tmp]["volta"]["Su"] = []
                myVariationList[tmp]["volta"]["Mo-Fr"].append(newT)
            else:
                myVariationList[ref]["volta"]["Mo-Fr"].append(t)
                debug_to_screen(len(t))
        while len(sa_ida) > 0:
            t = sa_ida[0]
            sa_ida.pop(0)
            debug_to_screen("(si) {0}".format(t), False)
            if len(t) > 5:
                newT = t[:5]
                variation = t[5:].strip()
                debug_to_screen("(si) Variation in \"{0}\"/\"{1}\"/\"{2}\"".format(t,newT,variation))
                if ignoreVariants:
                    if ref not in whitelistSet:
                        myVariationList[ref]["ida"]["Sa"].append(newT)
                tmp = u"{0} {1}".format(ref, variation)
                myVariations.append(variation)
                if variation not in variationSet:
                    variationSet.add(variation)
                    myVariationList[tmp] = {}
                    myVariationList[tmp]["ida"] = {}
                    myVariationList[tmp]["volta"] = {}
                    myVariationList[tmp]["ida"]["Mo-Fr"] = []
                    myVariationList[tmp]["volta"]["Mo-Fr"] = []
                    myVariationList[tmp]["ida"]["Sa"] = []
                    myVariationList[tmp]["volta"]["Sa"] = []
                    myVariationList[tmp]["ida"]["Su"] = []
                    myVariationList[tmp]["volta"]["Su"] = []
                myVariationList[tmp]["ida"]["Sa"].append(newT)
            else:
                myVariationList[ref]["ida"]["Sa"].append(t)
                debug_to_screen(len(t))
        while len(sa_volta) > 0:
            t = sa_volta[0]
            sa_volta.pop(0)
            debug_to_screen("(sv) {0}".format(t), False)
            if len(t) > 5:
                newT = t[:5]
                variation = t[5:].strip()
                debug_to_screen("(sv) Variation in \"{0}\"/\"{1}\"/\"{2}\"".format(t,newT,variation))
                if ignoreVariants:
                    if ref not in whitelistSet:
                        myVariationList[ref]["volta"]["Sa"].append(newT)
                tmp = u"{0} {1}".format(ref, variation)
                myVariations.append(variation)
                if variation not in variationSet:
                    variationSet.add(variation)
                    myVariationList[tmp] = {}
                    myVariationList[tmp]["ida"] = {}
                    myVariationList[tmp]["volta"] = {}
                    myVariationList[tmp]["ida"]["Mo-Fr"] = []
                    myVariationList[tmp]["volta"]["Mo-Fr"] = []
                    myVariationList[tmp]["ida"]["Sa"] = []
                    myVariationList[tmp]["volta"]["Sa"] = []
                    myVariationList[tmp]["ida"]["Su"] = []
                    myVariationList[tmp]["volta"]["Su"] = []
                myVariationList[tmp]["volta"]["Sa"].append(newT)
            else:
                myVariationList[ref]["volta"]["Sa"].append(t)
                debug_to_screen(len(t))
        while len(su_ida) > 0:
            t = su_ida[0]
            su_ida.pop(0)
            debug_to_screen("(di) {0}".format(t), False)
            if len(t) > 5:
                newT = t[:5]
                variation = t[5:].strip()
                debug_to_screen("(di) Variation in \"{0}\"/\"{1}\"/\"{2}\"".format(t,newT,variation))
                if ignoreVariants:
                    if ref not in whitelistSet:
                        myVariationList[ref]["ida"]["Su"].append(newT)
                myVariations.append(variation)
                tmp = u"{0} {1}".format(ref, variation)
                if variation not in variationSet:
                    variationSet.add(variation)
                    myVariationList[tmp] = {}
                    myVariationList[tmp]["ida"] = {}
                    myVariationList[tmp]["volta"] = {}
                    myVariationList[tmp]["ida"]["Mo-Fr"] = []
                    myVariationList[tmp]["volta"]["Mo-Fr"] = []
                    myVariationList[tmp]["ida"]["Sa"] = []
                    myVariationList[tmp]["volta"]["Sa"] = []
                    myVariationList[tmp]["ida"]["Su"] = []
                    myVariationList[tmp]["volta"]["Su"] = []
                myVariationList[tmp]["ida"]["Su"].append(newT)
            else:
                debug_to_screen(len(t))
                myVariationList[ref]["ida"]["Su"].append(t)
        while len(su_volta) > 0:
            t = su_volta[0]
            su_volta.pop(0)
            debug_to_screen("(dv) {0}".format(t), False)
            if len(t) > 5:
                newT = t[:5]
                variation = t[5:].strip()
                debug_to_screen("(dv) Variation in \"{0}\"/\"{1}\"/\"{2}\"".format(t,newT,variation))
                if ignoreVariants:
                    if ref not in whitelistSet:
                        myVariationList[ref]["volta"]["Su"].append(newT)
                tmp = u"{0} {1}".format(ref, variation)
                myVariations.append(variation)
                if variation not in variationSet:
                    variationSet.add(variation)
                    myVariationList[tmp] = {}
                    myVariationList[tmp]["ida"] = {}
                    myVariationList[tmp]["volta"] = {}
                    myVariationList[tmp]["ida"]["Mo-Fr"] = []
                    myVariationList[tmp]["volta"]["Mo-Fr"] = []
                    myVariationList[tmp]["ida"]["Sa"] = []
                    myVariationList[tmp]["volta"]["Sa"] = []
                    myVariationList[tmp]["ida"]["Su"] = []
                    myVariationList[tmp]["volta"]["Su"] = []
                myVariationList[tmp]["volta"]["Su"].append(newT)
            else:
                debug_to_screen(len(t))
                myVariationList[ref]["volta"]["Su"].append(t)
        durationIda = 60
        durationVolta = 60
        if len(myVariations) > 0:
            myVariations = uniq(myVariations)
            logger.warning("Variations detected in %s: %s", ref, ", ".join(myVariations))
            debug_to_screen("Known variations: ",False)
            for i in myVariations:
                debug_to_screen( "{0}, ".format(i),False)
                tmp = u"{0} {1}".format(ref, i)
                try:
                    if blacklistVariants and durationsList[tmp][0] < 0 and durationsList[tmp][1] < 0:
                        myRoutes["blacklist"].append(tmp)
                        logger.info("Route \"%s\" added to blacklist", tmp)
                except:
                    pass
                durationIda = 60
                durationVolta = 60
                try:
                    if durationsList[tmp][0] > 0:
                        durationIda = durationsList[ref][0]
                except:
                    durationIda = 60
                try:
                    if durationsList[tmp][1] > 0:
                        durationVolta = durationsList[ref][1]
                except:
                    durationVolta = 60
                myRoutes["routes"][tmp] = []
                myDays = [ u"Mo-Fr", u"Sa", u"Su" ]
                for d in myDays:
                    myRoutes = create_json(myRoutes, cal, tmp, origin, destination, d, myVariationList[tmp]["ida"][d], durationIda)
                    myRoutes = create_json(myRoutes, cal, tmp, destination, origin, d, myVariationList[tmp]["volta"][d], durationVolta)
            debug_to_screen("")
        durationIda = 60
        durationVolta = 60
        try:
            if durationsList[ref][0] > 0:
                durationIda = durationsList[ref][0]
        except:
            durationIda = 60
        try:
            if durationsList[ref][1] > 0:
                durationVolta = durationsList[ref][1]
        except:
            durationVolta = 60
        myRoutes["routes"][ref] = []
        myDays = [ u"Mo-Fr", u"Sa", u"Su" ]
        for d in myDays:
            myRoutes = create_json(myRoutes, cal, ref, origin, destination, d, myVariationList[ref]["ida"][d], durationIda)
            myRoutes = create_json(myRoutes, cal, ref, destination, origin, d, myVariationList[ref]["volta"][d], durationVolta)

newBlacklist = uniq(myRoutes["blacklist"])
newBlacklist.sort()

for wl in whitelisted:
    try:
        newBlacklist.remove(wl)
        logger.warning("%s removed from blacklist", wl)
    except:
        logger.error("Something went wrong: %s is not blacklisted", wl)
        pass

myRoutes["blacklist"] = newBlacklist
logger.info("Complete blacklist: %s", ", ".join(newBlacklist))

with open('times.json', 'w') as outfile:
    json.dump(myRoutes, outfile, sort_keys=True, indent=4)






