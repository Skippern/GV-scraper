#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Common functions
import os, sys
import requests
lib_path = os.path.abspath( os.path.join( '..', '..', 'lib' ) )
sys.path.append(lib_path)
from commons import *
from routing import *
from feriados import *
from make_json import *

debugMe = False

def lower_capitalized(input):
    output = lower_capitalized_master(input)
    # Specific place names
    return output.strip()

def getLines():
    r = False
    while r == False:
        try:
            r = requests.get("http://www.viacaosanremo.com.br/horarios/", timeout=30)
        except:
            r = False
    myList = []
    for item in r.content.split("\""):
        if item.find(".pdf") > 0:
            for word in item.split("/"):
                if word.find(".pdf") and len(word) == 7:
                    myList.append(word.split(".")[0])
    return myList
