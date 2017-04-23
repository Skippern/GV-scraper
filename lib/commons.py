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

def lower_capitalized_master(input):
    newString = input.lower().replace(u"/", u" / ").replace(u".", u". ").replace(u"-", u" - ")
    toOutput = []
    for s in newString.split(u" "):
        tmp = s.capitalize()
        toOutput.append(tmp)
    newString = u" ".join(toOutput)
    output = newString.replace(u" Da ", u" da ").replace(u" Das ", u" das ").replace(u" De ", u" de ").replace(u" Do ", u" do ").replace(u" Dos ", u" dos ").replace(u" E ", u" e ").replace(u" X ", u" x ").replace(u" Via ", u" via ").replace(u"º", u"º ").replace(u"ª", u"ª ").replace(u"  ", u" ").replace(u"  ", u" ").replace(u"  ", u" ").replace(u" .", u".")
    # Specific place names
    output = output.replace(u"Br101", u"BR-101")
    output = output.replace(u"Br 101", u"BR-101")
    output = output.replace(u"Br - 101", u"BR-101")
    output = output.replace(u"Br 262", u"BR-262")
    output = output.replace(u"Br - 262", u"BR-262")
    output = output.replace(u"Es 010", u"ES-010")
    output = output.replace(u"Es - 010", u"ES-010")
    output = output.replace(u"Iii", u"III")
    output = output.replace(u"Ii", u"II")
    output = output.replace(u"T.", u"Terminal")
    output = output.replace(u"Pç", u"Praça")
    output = output.replace(u"Av.", u"Avenida")
    output = output.replace(u"Av ", u"Avenida ")
    output = output.replace(u"Rod.", u"Rodovia")
    output = output.replace(u"Rod ", u"Rodovia ")
    output = output.replace(u"Mal.", u"Marechal")
    output = output.replace(u"Cel.", u"Coronel")
    output = output.replace(u"Rodoviaria", u"Rodoviária")
    output = output.replace(u"3º", u"3ª")
    output = output.replace(u"Hosp.", u"Hospital")
    output = output.replace(u"Parq.", u"Parque")
    output = output.replace(u"Ufes", u"UFES")
    output = output.replace(u"Ifes", u"IFES")
    output = output.replace(u"U. V. V.", u"UVV")
    return output.strip()

def debug_to_screen(text, newLine=True):
    if debugMe:
        if newLine:
            print text
        else:
            print text,

