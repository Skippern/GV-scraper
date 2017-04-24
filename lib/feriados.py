#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to get holidays and atypical workdays for use with exceptions in osm2gtfs
# if ical is needed, see link webcal://icalx.com/public/koesjan/BrazilianHolidays.ics
#from common import *

from datetime import date
from datetime import timedelta
from workalendar.america import Brazil
from workalendar.core import MON, TUE, WED,THU, FRI, SAT, SUN

class EspiritoSanto(Brazil):
    "Espírito Santo"
    FIXED_HOLIDAYS = Brazil.FIXED_HOLIDAYS + (
        (10, 28, u"Dia do Servidor Público"),
    )
    def holidays(self, year=None):
        if year == None:
            year = date.today().year
        try:
            return self.get_fixed_holidays(year) + self.get_variable_days(year)
        except:
            if self.get_variable_days(year) == None:
                return self.get_fixed_holidays(year)
                print "Variable holidays == None"
            if self.get_fixed_holidays(year) == None:
                print "Fixed holidays == None"
                return self.get_variable_days(year)
            return []
    include_carnaval = False
    def get_carnaval(self, year):
        return (self.get_easter_sunday(year) - timedelta(days=47))
    def get_variable_days(self, year):
        days = super(EspiritoSanto, self).get_variable_days(year)
        if self.include_carnaval:
            days.append((self.get_carnaval(year), "Carnaval"))
        #        days.extend([
        #        ])
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
                retValue.append( ( i[0] + timedelta(days=1), "Atypical working day") )
            elif self.is_working_day(i[0] - timedelta(days=1)) and not self.is_working_day(i[0] - timedelta(days=2)):
                retValue.append( ( i[0] - timedelta(days=1), "Atypical working day") )
        return retValue


class Cariacica(EspiritoSanto):
    "Cariacica"
    FIXED_HOLIDAYS = EspiritoSanto.FIXED_HOLIDAYS + (
        (4, 13, u"Nossa Senhora da Penha"),
        (6, 24, u"São João Batista / Aniversãrio de Cariacica"),
    )
    include_good_friday = True
    include_corpus_christie = True

class Guarapari(EspiritoSanto):
    "Guarapari"
    FIXED_HOLIDAYS = EspiritoSanto.FIXED_HOLIDAYS + (
        (6, 29, u"São Pedro"),
        (9, 19, u"Emanipação de Guarapari"),
        (12, 8, u"Nossa Senhora Conceição"),
    )

class Serra(EspiritoSanto):
    "Serra"
    FIXED_HOLIDAYS = EspiritoSanto.FIXED_HOLIDAYS + (
        (6, 29, u"São Pedro"),
        (12, 8, u"Nossa Senhora Conceição"),
        (12, 26, u"Dia do Serrano"),
    )
    include_good_friday = True
    include_corpus_christie = True
    include_ash_wednesday = True

class Viana(EspiritoSanto):
    "Viana"
    FIXED_HOLIDAYS = EspiritoSanto.FIXED_HOLIDAYS + (
        (7, 8, u""),
        (7, 23, u""),
        (8, 28, u""),
        (9, 8, u""),
        (12, 8, u""),
    )

class VilaVelha(EspiritoSanto):
    "Vila Velha"
    FIXED_HOLIDAYS = EspiritoSanto.FIXED_HOLIDAYS + (
        (5, 23, u"Colonização do Solo Espírito-santense"),
    )

class Vitoria(EspiritoSanto):
    "Vitória"
    FIXED_HOLIDAYS = EspiritoSanto.FIXED_HOLIDAYS + (
        (4, 24, u"Nossa Senhora da Penha"),
        (9, 8, u"Nossa Senhora da Vitória"),
    )
    include_good_friday = True
    include_corpus_christie = True
    include_carnaval = True

# Manually adding holidays from https://github.com/novafloss/workalendar/issues/187

#MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
#weekday_name = [ "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" ]
