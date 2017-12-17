#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Common functions
import os, sys
import requests
from bs4 import BeautifulSoup
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
    output = output.replace(u"B. Jesus Norte", u"Bom Jesus do Norte")
    output = output.replace(u"Cach. Itapemirim", u"Cachoeiro de Itapemirim")
    output = output.replace(u"Conc. Castelo", u"Conceição do Castelo")
    output = output.replace(u"V. Nova", u"Venda Nova do Imigrante")
    output = output.replace(u"Venda Nova Img.", u"Venda Nova do Imigrante")
    output = output.replace(u"B. Horizonte", u"Belo Horizonte")
    output = output.replace(u"Belem", u"Belém")
    output = output.replace(u"Vv", u"Vila Velha")
    output = output.replace(u"Sta Luzia", "Santa Luzia")
    output = output.replace(u"[conv]", u"[CONV]")
    output = output.replace(u"[exec]", u"[EXEC]")
    output = output.replace(u"[semi Direto]", u"[SEMI DIRETO]")
    return output.strip()

def getLines():
    r = False
    while r == False:
        try:
            r = requests.get("http://www.viacaoplaneta-es.com.br/destinos-e-horarios-viacao-planeta/", timeout=30)
        except:
            r = False
    htmlRaw = r.content.decode("UTF-8")
    soup = BeautifulSoup( htmlRaw, "lxml" )
    select = soup.find("select")
    options = [ option for option in select.find_all("option")]
    retValue = []
    seen = set()
    for o in options:
        try:
            if o.attrs["value"] not in seen:
                retValue.append( (o.attrs["value"], lower_capitalized(o.text), o.attrs["nome"]) )
                seen.add(o.attrs["value"])
        except:
            pass
    return retValue

def get_destination(tmp):
    destination = None
    while destination == None:
        if tmp[0].find("via") > 0:
            tmp = tmp[0].split("via")
            return tmp.pop(0)
            break
        tmp = tmp[0].split(" ")
        if tmp[-1] == u"[CONV]" or tmp[-1] == u"[EXEC]" or tmp[-1]:
            tmp.pop(-1)
        try:
            tmp.remove(u"")
        except:
            pass
        try:
            tmp.remove(u"BR-101")
        except:
            pass
        try:
            tmp.remove(u"ES-060")
        except:
            pass
        try:
            tmp.remove(u"DIRETO]")
        except:
            pass
        try:
            tmp.remove(u"[SEMI")
        except:
            pass
        tmp = " ".join(tmp).split("/")
        try:
            if len(tmp) > 1:
                tmp.pop(-1)
        except:
            pass
        tmp = " ".join(tmp).split(" ")
        if tmp[-1].find("BR-101") > 0 or tmp[-1].find("ES-060") > 0 or tmp[-1] == "BR-101" or tmp[-1] == "ES-060":
            tmp.pop(-1)
        tmp = " ".join(tmp).split(" - ")
        if len(tmp) == 1:
            return tmp[0]
            break
    return destination
