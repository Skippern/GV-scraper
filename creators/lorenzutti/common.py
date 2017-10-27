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
    output = output.replace(u"Sesc", u"SESC").replace(u"sesc", u"SESC")
    output = output.replace(u"Trevo Setiba", u"Trevo de Setiba")
    output = output.replace(u"Trevo BR-101", u"Trevo da BR-101")
    output = output.replace(u"Santa Monica", u"Santa Mônica")
    output = output.replace(u"Pontal Santa Mônica", u"Pontal de Santa Mônica")
    output = output.replace(u"Vitoria", u"Vitória")
    output = output.replace(u"Praça Vitória", u"Praça da Vitória")
    output = output.replace(u"Centro (pç Vitória)", u"Praça da Vitória")
    output = output.replace(u"Pç Vitória", u"Praça da Vitória")
    output = output.replace(u"Ewerson de A. Sodré", u"Ewerson de Abreu Sodré")
    output = output.replace(u"Meaipe", u"Meaípe")
    output = output.replace(u"J. Boa Vista", u"Jardim Boa Vista")
    output = output.replace(u"Jabarai", u"Jabaraí")
    output = output.replace(u"olaria", u"Olaria")
    output = output.replace(u"muquiçaba", u"Muquiçaba")
    output = output.replace(u"Independencia", u"Independência")
    output = output.replace(u"Patura", u"Paturá")
    output = output.replace(u"Iguape", u"Iguapé")
    output = output.replace(u"Ciac", u"CIAC")
    output = output.replace(u"Caic", u"CAIC")
    output = output.replace(u"N. S. ", u"Nossa Senhora da ")
    output = output.replace(u"Kubitischejk", u"Kubitschek")
    return output.strip()

def getLines():
    r = False
    while r == False:
        try:
            r = requests.get("http://www.expressolorenzutti.com.br/horarios/", timeout=30)
        except:
            r = False
    myList = []
    if not isinstance(r.content, unicode):
        myContent = r.content
        codec = 'utf-8'
        try:
            encoding = charset.detect(myContent)
            codec = encoding['encoding']
            try:
                myContent = myContent.encode(codec).decode('utf-8')
            except:
                pass
        except:
            pass
    for item in myContent.split("\""):
        if item.find(".pdf") > 0:
            for word in item.split("/"):
                if word.find(".pdf") and len(word) == 7:
                    myList.append(word.split(".")[0])
    return myList

def download_pdf(i):
    baseurl = "http://www.expressolorenzutti.com.br/"
    asseturl = baseurl + "assets/horarios/"
    downloadURL = asseturl + i + ".pdf"
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
            logger.info("No file downloaded for %s, skipping", i)
            return None
    else:
        logger.info("No file downloaded for %s, skipping", i)
        return None

