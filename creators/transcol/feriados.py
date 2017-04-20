#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to get holidays and atypical workdays for use with exceptions in osm2gtfs
# if ical is needed, see link webcal://icalx.com/public/koesjan/BrazilianHolidays.ics
#from common import *

from datetime import date
from datetime import timedelta
from workalendar.america import Brazil

cal = Brazil()
# Manually adding holidays from https://github.com/novafloss/workalendar/issues/187
include_carnaval = True
include_serra = False
include_guarapari = False
include_cariacica = False
include_viana = False
include_vila_velha = False
include_vitoria = False

cal.include_good_friday = True
cal.include_corpus_christie = True
cal.include_ash_wednesday = True

carnaval = (cal.get_easter_sunday(2017) - timedelta(days=47))
carnavalM = (cal.get_easter_sunday(2017) - timedelta(days=48))

if include_serra:
#    include_carnaval = True
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (6, 29, u"São Pedro"), ) # Serra
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (12, 8, u"Nossa Senhora Conceição"), ) # Serra
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (12, 26, u"Dia do Serrano"), ) # Serra
if include_vitoria:
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (4, 24, u"Nossa Senhora da Penha"), ) # Vitoria
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (9, 8, u"Nossa Senhora da Vitória"), ) # Vitoria
if include_vila_velha:
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (5, 23, u"Colonização do Solo Espírito-santense"), ) # Vila Velha
if include_viana:
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (7, 8, u""), ) # Viana
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (7, 23, u""), ) # Viana
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (8, 28, u""), ) # Viana
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (9, 8, u""), ) # Viana
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (12, 8, u""), ) # Viana
if include_cariacica:
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (4, 13, u"Nossa Senhora da Penha"), ) # Cariacica
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (6, 24, u"São João Batista / Aniversãrio de Cariacica"), ) # Cariacica
if include_guarapari:
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (6, 29, u"São Pedro"), ) # Guarapari
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (9, 19, u"Emanipação de Guarapari"), ) # Guarapari
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (12, 8, u"Nossa Senhora Conceição"), ) # Guarapari
if include_carnaval:
    if include_serra:
        cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (carnavalM.month, carnavalM.day, "Carnaval"), ) # Serra
    cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (carnaval.month, carnaval.day, "Carnaval"), ) # Serra
cal.FIXED_HOLIDAYS = cal.FIXED_HOLIDAYS + ( (10, 28, u"Dia do Servidor Público"), ) # ES

###
MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
weekday_name = [ "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" ]
atypical_days = []
saturday_holidays = []
weekday_holidays = []
sunday_holidays = []
#print cal.FIXED_HOLIDAYS

def stringify(date_array):
    retValue = []
    for myDate in date_array:
        #        print myDate
        try:
            retValue.append(str(myDate[0]))
        except:
            pass
    return retValue

for i in cal.holidays():
    if i[0].weekday() == SAT:
        saturday_holidays.append(i)
    elif i[0].weekday() == SUN:
        sunday_holidays.append(i)
    else:
        weekday_holidays.append(i)
        if i[0].weekday() == TUE:
            testday = i[0] - timedelta(days=1)
            if not cal.is_holiday(testday):
                atypical_days.append( (testday, "Atypical weekday") )
        elif i[0].weekday() == THU:
            testday = i[0] + timedelta(days=1)
            if not cal.is_holiday(testday):
                atypical_days.append( (testday, "Atypical weekday") )

def get_atypical_days():
    return stringify(atypical_days)
def get_saturday_holidays():
    return stringify(saturday_holidays)
def get_weekday_holidays():
    return stringify(weekday_holidays)
def get_sunday_holidays():
    return stringify(sunday_holidays)

