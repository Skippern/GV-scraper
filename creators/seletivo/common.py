#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Common functions
import os, sys
lib_path = os.path.abspath( os.path.join( '..', '..', 'lib' ) )
sys.path.append(lib_path)
from commons import *
from routing import *
from feriados import *
from make_json import *

def lower_capitalized(input):
    output = lower_capitalized_master(input)
    # Specific place names
    output = output.replace(u"P. Itapoã", u"Praia de Itapoã")
    output = output.replace(u"Beira M", u"Beira Mar").replace(u"Marar", u"Mar")
    output = output.replace(u"B. Mar", u"Beira Mar")
    output = output.replace(u"C. Itaparica", u"Coqueiral de Itaparica")
    output = output.replace(u"Exp.", u"Expedito")
    output = output.replace(u"J. Camburi", u"Jardim Camburi")
    output = output.replace(u"P. Costa", u"Praia da Costa")
    output = output.replace(u"S. Dourada", u"Serra Dourada")
    output = output.replace(u"M. Noronha", u"Marcilio de Noronha")
    return output.strip()

def getLines():
    downloadURL = "https://sistemas.es.gov.br/webservices/ceturb/onibus/api/ConsultaLinha?Tipo_Linha=Seletivo"
    routes = []
    myJSON = None
    r = False
    while r == False:
        try:
            r = requests.get(downloadURL, timeout=30)
        except requests.exceptions.ReadTimeout as e:
            r = False
        except requests.exceptions.ConnectionError as e:
            r = False
        try:
            myJSON = json.dumps(json.loads(r.content))
        except:
            r = False
    for i in json.loads(myJSON):
        routes.append( [ str(int(i[u"Linha"])), lower_capitalized(unicode(i[u"Descricao"])) ] )
    return routes
