#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Common functions


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
    output = output.replace(u"Br ", u"BR-").replace(u"Br-", u"BR-").replace(u"Br1", u"BR-1")
    output = output.replace(u"Sesc", u"SESC").replace(u"sesc", u"SESC")
    output = output.replace(u"Trevo Setiba", u"Trevo de Setiba")
    output = output.replace(u"Trevo BR-101", u"Trevo da BR-101")
    output = output.replace(u"Santa Monica", u"Santa Mônica")
    output = output.replace(u"Pontal Santa Mônica", u"Pontal de Santa Mônica")
    output = output.replace(u"Vitoria", u"Vitória")
    output = output.replace(u"Praça Vitória", u"Praça da Vitória")
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
    return output.strip()

def debug_to_screen(text, newLine=True):
    if debugMe:
        if newLine:
            print text
        else:
            print text,

