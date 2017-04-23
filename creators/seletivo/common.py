#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Common functions
import os, sys
lib_path = os.path.abspath( os.path.join( '..', '..', 'lib' ) )
sys.path.append(lib_path)
from commons import *
from routing import *

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

