#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Common functions
from overpasser import *

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
    output = output.replace(u"Br262", u"BR-262")
    output = output.replace(u"Br 262", u"BR-262")
    output = output.replace(u"Br - 262", u"BR-262")
    output = output.replace(u"Es010", u"ES-010")
    output = output.replace(u"Es 010", u"ES-010")
    output = output.replace(u"Es - 010", u"ES-010")
    output = output.replace(u"Es060", u"ES-060")
    output = output.replace(u"Es 060", u"ES-060")
    output = output.replace(u"Es - 060", u"ES-060")
    output = output.replace(u"Iii", u"III")
    output = output.replace(u"Ii", u"II")
    output = output.replace(u"T.", u"Terminal")
    output = output.replace(u"Pç", u"Praça")
    output = output.replace(u"Praçaa", u"Praça")
    output = output.replace(u"Praça.", u"Praça")
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
    output = output.replace(u"Shoping", u"Shopping")
    return output.strip()

def debug_to_screen(text, newLine=True):
    if debugMe:
        if newLine:
            print text
        else:
            print text,

def stringify_date(date):
    return str(date)
    retValue = []
    for myDate in date_array:
        #        print myDate
        try:
            retValue.append(str(myDate[0]))
        except:
            pass
    return retValue

def calculate_end_time(start_time, duration):
    if duration < 1:
        duration = 60
    end_time = start_time
    day = 0
    hr = int(start_time[:2])
    min = int(start_time[3:])
    min += duration
    while min > 59:
        hr += 1
        min -= 60
    while hr > 23:
        hr -= 24 # Should we put a day+1 variable as well?
        day += 1
    end_time = u"{0}:{1}".format(str(hr).zfill(2), str(min).zfill(2))
    if day > 0:
        end_time = u"{0}+{1}".format(end_time, str(day))
    return end_time


