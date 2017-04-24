#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to download time tables as PDF and calculate route durations based on relations for the routes in OpenStreetMap
from commons import *

import os
import sys
import io
import logging
import requests
import json
import datetime
import time
from unidecode import unidecode

logger = logging.getLogger("GTFS_make_json")

def create_json(myRoutes, cal, ref, fromV, toV, d, times, duration=60, atypical=False):
    try:
        test = myRoutes["routes"]
    except:
        myRoutes[u"routes"] = {}
    try:
        test = myRoutes["routes"][ref]
    except:
        myRoutes[u"routes"][ref] = []
    try:
        debug_to_screen(u"{0} - {1} -> {2} ({3}) {4} - {5}".format(ref, fromV, toV, d, len(times), duration))
    except:
        debug_to_screen("In make_json, times TypeError, have no len()")
    times.sort()
    retValue = {}
    retValue[u"from"] = fromV
    retValue[u"to"] = toV
    retValue[u"service"] = []
    retValue[u"exceptions"] = []
    service = []
    exceptions = []
    if d == "Su":
    #        retValue[u"service"] = [ d ]
        service.append(d)
        for i in cal.get_saturday_holidays():
            service.append(stringify_date(i[0]))
        for i in cal.get_weekday_holidays():
            service.append(stringify_date(i[0]))
    elif d == "Sa":
        service.append(d)
        for i in cal.get_saturday_holidays():
            exceptions.append(stringify_date(i[0]))
    elif d == "Ex":
        for i in cal.get_atypical_workdays():
            service.append(stringify_date(i[0]))
    else:
        service.append(d)
        if atypical == True:
            for i in cal.get_weekday_holidays():
                exceptions.append(stringify_date(i[0]))
            for i in cal.get_atypical_workdays():
                exceptions.append(stringify_date(i[0]))
        else:
            for i in cal.get_weekday_holidays():
                exceptions.append(stringify_date(i[0]))
    retValue[u"service"] = service
    retValue[u"exceptions"] = exceptions
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
    return myRoutes
