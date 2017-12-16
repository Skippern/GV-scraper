#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to get holidays and atypical workdays for use with exceptions in osm2gtfs
# if ical is needed, see link webcal://icalx.com/public/koesjan/BrazilianHolidays.ics
#from common import *

from datetime import date
from datetime import timedelta
from workalendar.america import Brazil, BrazilEspiritoSanto, BrazilVilaVelhaCity, BrazilVitoriaCity, BrazilCariacicaCity, BrazilGuarapariCity, BrazilSerraCity
from workalendar.core import MON, TUE, WED,THU, FRI, SAT, SUN, Calendar, WesternCalendar

class CalendarNull(Calendar):
    "NULL"
    def get_saturday_holidays(self, year=None):
        retValue = []
        for i in self.holidays(year):
            if i[0].weekday() == SAT:
                retValue.append(i)
        return retValue
    def get_weekday_holidays(self, year=None):
        retValue = []
        for i in self.holidays(year):
            if i[0].weekday() != SAT and i[0].weekday() != SUN:
                retValue.append(i)
        return retValue
    def get_sunday_holidays(self, year=None):
        retValue = []
        for i in self.holidays(year):
            if i[0].weekday() == SUN:
                retValue.append(i)
        return retValue
    def get_atypical_workdays(self, year=None):
        retValue = []
        for i in self.holidays(year):
            if self.is_working_day(i[0] + timedelta(days=1)) and not self.is_working_day(i[0] + timedelta(days=2)):
                retValue.append( ( i[0] + timedelta(days=1), u"Atypical working day") )
            elif self.is_working_day(i[0] - timedelta(days=1)) and not self.is_working_day(i[0] - timedelta(days=2)):
                retValue.append( ( i[0] - timedelta(days=1), u"Atypical working day") )
        return retValue

class EspiritoSanto(BrazilEspiritoSanto, CalendarNull):
    "Espírito Santo"

class Cariacica(BrazilCariacicaCity, EspiritoSanto):
    "Cariacica"

class Guarapari(BrazilGuarapariCity, EspiritoSanto):
    "Guarapari"

class Serra(BrazilSerraCity, EspiritoSanto):
    "Serra"

class Viana(EspiritoSanto):
    "Viana"
    FIXED_HOLIDAYS = EspiritoSanto.FIXED_HOLIDAYS + (
        (7, 8, u""),
        (7, 23, u""),
        (8, 28, u""),
        (9, 8, u""),
        (12, 8, u""),
    )

class VilaVelha(BrazilVilaVelhaCity, EspiritoSanto):
    "Vila Velha"

class Vitoria(BrazilVitoriaCity, EspiritoSanto):
    "Vitória"
