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
from bs4 import BeautifulSoup

logger = logging.getLogger("GTFS_get_times")
logging.basicConfig(filename="/var/log/GTFS/viacao-gv.log", level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s - %(message)s", datefmt="%Y/%m/%d %H:%M:%S:")

cal = Vitoria()

# PDFs are stored here
baseurl = "http://sistemas.vitoria.es.gov.br/redeiti/"

debugMe = False

# List of route numbers
linheList = []

config = {}
with open('viacao-gv.json', 'r') as infile:
    config = json.load(infile)

myRoutes = {}
durationsList = {}
try:
    with open('durations.json', 'r') as infile:
        durationsList = json.load(infile)
except:
    pass
myRoutes[u"updated"] = str(datetime.date.today())
myRoutes[u"operator"] = u"Viação Grande Vitória"
myRoutes[u"network"] = u"PMV"
myRoutes[u"source"] = baseurl
myRoutes[u"excluded_lines"] = []

for i in getLines():
    name = i[1]
    tmp = name.split(u"/")
    if len(tmp) > 2 and name.find(u"via") < 0:
        tmp[-1] = u"{0} (Circular)".format(tmp[-1]).replace(u"(Circular) (Circular)", u"(Circular)")
    if len(tmp) == 1:
        tmp = tmp[0].split(u"via")
        origin = tmp.pop(0)
        destination = origin
    else:
        origin = tmp.pop(0)
        if tmp[0].find(u"via") > 0:
            tmp = tmp[0].split("via")
        if tmp[0] == u"" or tmp[0] == u" ":
            destination = origin
        elif tmp[-1].find(u"Circular") > 0:
            destination = tmp.pop(len(tmp)-2)
        else:
            destination = tmp.pop(0)
    try:
        tmp = destination.split(u" ")
        tmp.remove(u"Circular")
        destination = u" ".join(tmp)
    except:
        pass
    origin = origin.strip()
    destination = destination.strip()
    r = False
    timeURL = baseurl + u"listarHorario.cfm?cdLinha=" + i[0]
    logger.debug(timeURL)
    while not r:
        try:
            r = requests.get(timeURL, timeout=30)
        except:
            r = False
    output = unicode(r.content.decode("UTF-8"))
    soup = BeautifulSoup(output, "lxml")
    tables = soup.find_all('table')
    if len(tables) > 3:
        print u"!!!!! We have {0} tables !!!!".format(len(tables))
    tableJSON = {}
    for table in tables:
        header = table.th.text.strip()
        times = [td.text.strip() for td in table.find_all('td')]
        tableJSON[header] = []
        for t in times:
            if t != u'' and t != u'Não circula' and t != u' ':
                tableJSON[header].append(t)
        tableJSON[header].sort()
    if durationsList[i[0]][0] < 0 and durationsList[i[0]][1] < 0:
        logger.debug(u"Negative duration on route \"%s\", adding to blacklist", i[0])
        myRoutes[u"excluded_lines"].append(i[0])
        continue
    try:
        myRoutes = create_json(myRoutes, cal, i[0], origin, destination, u"Mo-Fr", tableJSON[u"Segunda a Sexta"], durationsList[i[0]][0])
    except:
        pass
    try:
        myRoutes = create_json(myRoutes, cal, i[0], origin, destination, u"Sa", tableJSON[u"Sábado"], durationsList[i[0]][0])
    except:
        pass
    try:
        myRoutes = create_json(myRoutes, cal, i[0], origin, destination, u"Su", tableJSON[u"Domingo"], durationsList[i[0]][0])
    except:
        pass

newBlacklist = uniq(myRoutes[u"excluded_lines"])
newBlacklist.sort()
myRoutes[u"excluded_lines"] = newBlacklist
logger.info(u"Complete blacklist: %s", u", ".join(newBlacklist))

with open('times.json', 'wb') as outfile:
    json.dump(myRoutes, outfile, sort_keys=True, indent=4)






