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
    output = output.replace(u" x ", u" / ")
    output = output.replace(u"D'arc", u"d'Arc")
    output = output.replace(u"Jd", u"Jardim")
    output = output.replace(u"via da Penha", u"via Reta da Penha")
    output = output.replace(u"Shoppingvitoria", u"Shopping Vitória")
    output = output.replace(u"(circular)", u"(Circular)")
    output = output.replace(u"(noturno)", u"(Noturno)")
    output = output.replace(u"Shop.", u"Shopping")
    output = output.replace(u"Vitoria", u"Vitória")
    output = output.replace(u"Mario Cypreste", u"Mário Cypreste")
    return output.strip()

