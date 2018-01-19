#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This is to check and print a list of outdated data sources
import os
import json
import requests
#import unidecode
#import chardet

sources = []

for f in os.listdir(os.getcwd()):
    try:
        filename, fileExtension = f.split('.')
        if fileExtension == 'json':
            sources.append(f)
    except:
        pass

status = {}

for s in sources:
    my = {}
    with open(s, 'r') as infile:
        my = json.load(infile)

    status[my['operator']] = {}
    status[my['operator']][u"operator"] = my["operator"]
    status[my['operator']][u"updated"] = my['updated']
    status[my['operator']][u"id"] = my['operator:ref']
    status[my['operator']][u"source"] = my['updated']
    status[my['operator']][u"url"] = "https://sistemas.es.gov.br/der/servicos/arquivos/transporte/horarios/HR1512479832.pdf"

htmlStatus = 0
while htmlStatus != 200:
    html = requests.get('https://der.es.gov.br/quadro-de-horarios')
    htmlStatus = html.status_code
## Here we need to get .js generated content
with open('der-es.html', 'w') as outfile:
    outfile.write(html.content)

for s in status:
    htmlStatus = 0
    pdf = None
    while htmlStatus != 200:
        r = requests.get(status[s][u'url'])
        if r.headers.get('content-length') > 0:
            pdf = r.content
        htmlStatus = html.status_code
    filename = 'PDF/{0}.pdf'.format(status[s][u'id'])
    with open(filename, 'wb') as outfile:
        outfile.write(pdf)

    if status[s]['updated'] != status[s]['source']:
#        print u"OUTDATED: {0} - {1} -> {2}".format(status[s]['id'], status[s]['updated'], status[s]['source'])
        print u"OUTDATED: {0}:{1} - {2} -> {3}".format(status[s]['id'], status[s]['operator'], status[s]['updated'], status[s]['source'])
    else:
#        print u"UP TO DATE: {0} - {1} = {2}".format(status[s]['id'], status[s]['updated'], status[s]['source'])
        print u"UP TO DATE: {0}:{1} - {2} -> {3}".format(status[s]['id'], status[s]['operator'], status[s]['updated'], status[s]['source'])
