#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Common functions
import os, sys
import requests
import json
lib_path = os.path.abspath( os.path.join( '..', '..', 'lib' ) )
sys.path.append(lib_path)
from commons import *
from overpasser import *
from routing import *
from feriados import *
from make_json import *

debugMe = False

def lower_capitalized(input):
    output = lower_capitalized_master(input)
    # Specific place names
    return output.strip()

def getLines():
    print u"Getting Lines from static DER-ES source:",
    with open("../../sources/der-es/mar_aberto.json", 'r') as f:
        lineSource = json.load(f)
    print lineSource["operator"]

    myList = []

    for r in lineSource['routes'].keys():
        for trip in lineSource['routes'][r]:
            myString = ""
            try:
                myString = myString + trip['ref'] + " "
                ref = trip['ref']
            except:
                myString = myString + r + " "
                ref = r
                pass
            origin = trip['from']
            destination = trip['to']
            myString = myString + trip['from'] + " x " + trip['to']
            try:
                via = trip['via']
                myString = myString + " via " + via
            except:
                via = None
            myList.append( (ref, origin, destination, via ) )
    myList = uniq(myList)
    myrefs = []
    for i in myList:
        myrefs.append(i[0])
    myrefs = uniq(myrefs)
    print u"Routes found: ", myrefs
    return myList


