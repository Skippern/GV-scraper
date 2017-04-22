#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Common functions

debugMe = False

def uniq(values):
    output = []
    seen = set()
    for value in values:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

def lower_capitalized(input):
    newString = input.lower().replace(u"/", u" / ").replace(u".", u". ").replace(u"-", u" - ")
    toOutput = []
    for s in newString.split(u" "):
        tmp = s.capitalize()
        toOutput.append(tmp)
    newString = u" ".join(toOutput)
    output = newString.replace(u" Da ", u" da ").replace(u" Das ", u" das ").replace(u" De ", u" de ").replace(u" Do ", u" do ").replace(u" Dos ", u" dos ").replace(u" E ", u" e ").replace(u" X ", u" x ").replace(u" Via ", u" via ").replace(u"  ", u" ").replace(u"ª", u"ª ").replace(u"  ", u" ").replace(u"  ", u" ")
    # Specific place names
    output = output.replace(u"P. Itapoã", u"Praia de Itapoã")
    output = output.replace(u"Beira M", u"Beira Mar").replace(u"Marar", u"Mar")
    output = output.replace(u"B. Mar", u"Beira Mar")
    output = output.replace(u"C. Itaparica", u"Coqueiral de Itaparica")
    output = output.replace(u"Ufes", u"UFES")
    output = output.replace(u"Exp.", u"Expedito")
    output = output.replace(u"J. Camburi", u"Jardim Camburi")
    output = output.replace(u"P. Costa", u"Praia da Costa")
    output = output.replace(u"Es 010", u"ES-010")
    output = output.replace(u"U. V. V.", u"UVV")
    output = output.replace(u"Rodoviaria", u"Rodoviária")
    output = output.replace(u"S. Dourada Iii", u"Serra Dourada III")
    output = output.replace(u"M. Noronha", u"Marcilio de Noronha")
    return output.strip()

def debug_to_screen(text, newLine=True):
    if debugMe:
        if newLine:
            print text
        else:
            print text,

