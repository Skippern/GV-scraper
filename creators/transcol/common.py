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

debugMe = False

def lower_capitalized(input):
    output = lower_capitalized_master(input)
    # Specific place names
    output = output.replace(u"(bike Gv)", u"(Bike GV)")
    output = output.replace(u"circular", u"Circular")
    output = output.replace(u"Exp.", u"Expedito")
    output = output.replace(u"Expd.", u"Expedito")
    output = output.replace(u"Beira M", u"Beira Mar").replace(u"Beira Marar", u"Beira Mar")
    output = output.replace(u"B. Mar", u"Beira Mar")
    output = output.replace(u"S. Dourada", u"Serra Dourada")
    output = output.replace(u"Jacaraipe", u"Jacaraípe")
    output = output.replace(u"Rodoviaria", u"Rodoviária")
    output = output.replace(u"P. Costa", u"Praia da Costa")
    output = output.replace(u"J. Camburi", u"Jardim Camburi")
    output = output.replace(u"M. Noronha", u"Marcilio de Noronha")
    output = output.replace(u"M. de Noronha", u"Marcilio de Noronha")
    output = output.replace(u"C. Itaperica", u"Condominio Itaparica")
    output = output.replace(u"P. Itapoã", u"Praia de Itapoã")
    output = output.replace(u"T Laranjeiras", u"Terminal Laranjeiras")
    output = output.replace(u"Praça Eucalipto", u"Praça do Eucalipto")
    output = output.replace(u"Itaciba", u"Utacibá")
    output = output.replace(u"Jacaraipe", u"Jacaraípe")
    output = output.replace(u"Torquatro", u"Torquato")
    output = output.replace(u"S. Torquato", u"São Torquato")
    output = output.replace(u"Darlysantos", u"Darly Santos")
    output = output.replace(u"Col. Laranjeiras", u"Colina de Laranjeiras")
    output = output.replace(u"B. República", u"Bairro República")
    output = output.replace(u"B. Ipanema", u"Bairro Ipanema")
    output = output.replace(u"B. Primavera", u"Bairro Primavera")
    output = output.replace(u"V. Bethânia", u"Vila Bethânia")
    output = output.replace(u"V. Encantado", u"Vale Encantado")
    output = output.replace(u"Heac", u"HEAC")
    output = output.replace(u"B. Carapebus", u"Bairro Carapebus")
    output = output.replace(u"C. Continental", "Cidade Continental")
    output = output.replace(u"S. Mônica", u"Santa Mônica")
    output = output.replace(u"R. Penha", u"Reta da Penha")
    output = output.replace(u"Paulo P. Gomes", u"Paulo Pereira Gomes")
    output = output.replace(u"C. Itaparica", u"Coqueiral de Itaparica")
    output = output.replace(u"C. Verde", u"Campo Verde")
    output = output.replace(u"P. Cariacica", u"Porto de Cariacica")
    output = output.replace(u"A. Ramos", u"Alzira Ramos")
    output = output.replace(u"Afb", "A. F. Borges")
    output = output.replace(u"A. F. Borges", "Antonio Ferreira Borges")
    output = output.replace(u"Norte/sul", u"Norte Sul")
    output = output.replace(u"Norte / Sul", u"Norte Sul")
    output = output.replace(u"Norte-sul", u"Norte Sul")
    output = output.replace(u"J. Penha", u"Jardim da Penha")
    output = output.replace(u"J. América", u"Jardim América")
    output = output.replace(u"J. America", u"Jardim América")
    output = output.replace(u"J. Marilândia", u"Jardim Marilândia")
    output = output.replace(u"Rod.", u"Rodovia")
    output = output.replace(u"Res.", u"Residencial")
    output = output.replace(u"Cdp", u"CDP")
    output = output.replace(u"Crefes", u"CREFES")
    output = output.replace(u"Ceasa", u"CEASA")
    output = output.replace(u"Ifes", u"IFES")
    output = output.replace(u"Civit", u"CIVIT")
    output = output.replace(u"V. N.", u"Vila Nova")
    output = output.replace(u"Psme", u"PSME")
    output = output.replace(u"Bl.", u"Balneário")
    output = output.replace(u"B - C - A", u"B-C-A")
    output = output.replace(u"(expresso)", u"- Expresso")
    output = output.replace(u"D`água", u"d`Água")
    return output.strip()

def getLines():
    downloadURL = "https://sistemas.es.gov.br/webservices/ceturb/onibus/api/ConsultaLinha/"
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
