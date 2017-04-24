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
#    newString = input.lower().replace(u"/", u" / ").replace(u".", u". ").replace(u"-", u" - ")
#    toOutput = []
#    for s in newString.split(u" "):
#        tmp = s.capitalize()
#        toOutput.append(tmp)
#    newString = u" ".join(toOutput)
#    output = newString.replace(u" Da ", u" da ").replace(u" Das ", u" das ").replace(u" De ", u" de ").replace(u" Do ", u" do ").replace(u" Dos ", u" dos ").replace(u" E ", u" e ").replace(u" X ", u" x ").replace(u" Via ", u" via ").replace(u"  ", u" ").replace(u"ª", u"ª ").replace(u"  ", u" ").replace(u"  ", u" ")
    # Specific place names
    output = output.replace(u" x ", u" / ")
#    output = output.replace(u"Av.", u"Avenida")
#    output = output.replace(u"Av ", u"Avenida ")
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

#def debug_to_screen(text, newLine=True):
#    if debugMe:
#        if newLine:
#            print text
#        else:
#            print text,

#def uniq(values):
#    output = []
#    seen = set()
#    for value in values:
#        if value not in seen:
#            output.append(value)
#            seen.add(value)
#    return output

