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
from unidecode import unidecode
from bs4 import BeautifulSoup

logger = logging.getLogger("GTFS_get_times")
logging.basicConfig(filename="/var/log/GTFS/planeta-es.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

cal = EspiritoSanto()
calNull = CalendarNull()

# PDFs are stored here
baseurl = "http://www.viacaoplaneta-es.com.br/destinos-e-horarios-viacao-planeta/"

#debugMe = True

config = {}
with open('planeta.json', 'r') as infile:
    config = json.load(infile)

myRoutes = {}
durationsList = {}
try:
    with open('durations.json', 'r') as infile:
        durationsList = json.load(infile)
except:
    pass
myRoutes[u"updated"] = str(datetime.date.today())
myRoutes[u"operator"] = u"Planeta"
myRoutes[u"network"] = u"Planeta"
myRoutes[u"source"] = baseurl
myRoutes[u"blacklist"] = []

for i in getLines():
    name = i[1]
    ref = i[0]
    print ref, name
    tmp = name.split(u" x ")
    origin = tmp.pop(0)
    destination = get_destination(tmp)
    origin = origin.strip()
    destination = destination.strip()
    print u"    From:", origin
    print u"    To:  ", destination
    logger.info(u"Route \"%s\" from %s to %s", ref, origin, destination)
    if durationsList[ref][0] < 0:
        debug_to_screen(u"Route \"{0}\" have negative duration and should be blacklisted".format(ref))
        logger.debug(u"Route \"%s\" have negative duration and should be blacklisted", ref)
        myRoutes[u"blacklist"].append(ref)
        continue
    timeURL = baseurl + ref + "/" + i[2]
    logger.debug(timeURL)
    r = False
    while r == False:
        try:
            r = requests.get(timeURL, timeout=30)
        except:
            r = False
    soup = BeautifulSoup(r.content.decode("UTF-8"), "lxml")
    li_all = soup.find_all("li")
    for li in li_all:
        try:
            xxx = li.attrs["class"][0]
            if xxx == "box" or xxx == u"box":
                xx = li.find("h2")
                days = lower_capitalized(xx.text)
                hour = []
                hour = [ div.text for div in li.find_all("div")]
                d = ""
                if days == u"Segunda A Sábado" or days == u"Segunda A Sabado" or days == u"Segunda À Sabado" or days == u"Segunda À Sábado" or days == u"Segunda A Sabádo":
                    d = "Mo-Sa"
                    debug_to_screen("d set to: {0}".format(d))
                elif days == u"Segunda A Sexta" or days == u"Segunda À Sexta":
                    d = "Mo-Fr"
                    debug_to_screen("d set to: {0}".format(d))
                elif days == u"Segunda A Domingo" or days == u"Diariamente" or days == u"Segunda À Domingo":
                    d = "Mo-Su"
                    debug_to_screen("d set to: {0}".format(d))
                elif days == u"Terça A Sábado":
                    d = "Tu-Sa"
                elif days == "Segunda Semi Direto":
                    d = "Mo"
                    debug_to_screen("d set to: {0}".format(d))
                elif days == "Sexta Semi Direto":
                    d = "Fr"
                    debug_to_screen("d set to: {0}".format(d))
                elif days == u"Sabado" or days == u"Sábado" or days == u"Sábados":
                    d = "Sa"
                    debug_to_screen("d set to: {0}".format(d))
                elif days == u"Domingos" or days == u"Domingo":
                    d = "Su"
                    debug_to_screen("d set to: {0}".format(d))
                elif days == u"Sex. Dom e Seg":
                    d = "Mo,Fr,Su"
                    debug_to_screen("d set to: {0}".format(d))
                elif days == u"Segundas e Sextas":
                    d = "Mo,Fr"
                    debug_to_screen("d set to: {0}".format(d))
                elif days == u"Sexta e Domingo" or days == u"Sextas e Domingo":
                    d = "Fr,Su"
                    debug_to_screen("d set to: {0}".format(d))
                else:
                    debug_to_screen("d NOT set: {0}".format(d))
                    logger.debug("d NOT set: %s", days)
                debug_to_screen( "d = \"{0}\"".format(d) )
                logger.debug("Route %s: d = \"%s\"", ref, d)
                if d != "":
                    debug_to_screen( u"create_json(myRoutes, calNull, \"{0}\", \"{1}\", \"{2}\", \"{3}\", [ {4} ], {5})".format(ref, origin, destination, d, hour, durationsList[ref][0]) )
                    myRoutes = create_json(myRoutes, calNull, ref, origin, destination, d, hour, durationsList[ref][0])
                else:
                    if days == u"Domingos e Feriados":
                        debug_to_screen( u"create_json(myRoutes, cal, \"{0}\", \"{1}\", \"{2}\", \"{3}\", [ {4} ], {5})".format(ref, origin, destination, "Su", hour, durationsList[ref][0]) )
                        logger.debug(u"Route %s: Have holidays and are added to \"Su\"", ref)
                        myRoutes = create_json(myRoutes, cal, ref, origin, destination, "Su", hour, durationsList[ref][0])
                    elif days == u"Domingos via Rio Novo" or days == "Somente Aos Dom (via Rio Novo)":
                        myRef = "{0}-1".format(ref)
                        logger.debug(u"Route %s: Passes Rio Novo on Sundays as variant \"%s\"", ref, myRef)
                        debug_to_screen( u"create_json(myRoutes, calNull, \"{0}\", \"{1}\", \"{2}\", \"{3}\", [ {4} ], {5})".format(myRef, origin, destination, "Su", hour, durationsList[myRef][0]) )
                        myRoutes = create_json(myRoutes, calNull, myRef, origin, destination, "Su", hour, durationsList[myRef][0])
                    else:
                        logger.error(u"\"%s\" not caught in days for route \"%s\"", days, ref)
            else:
                continue
        except KeyError:
            pass
        except:
            logger.error(u"Something went seriously wrong in parsing HTML :: BeautifulSoup cast error?")
            raise
            pass

newBlacklist = uniq(myRoutes[u"blacklist"])
newBlacklist.sort()
myRoutes[u"blacklist"] = newBlacklist
logger.info(u"Complete blacklist: %s", ", ".join(newBlacklist))

with open('times.json', 'wb') as outfile:
    json.dump(myRoutes, outfile, sort_keys=True, indent=4)






