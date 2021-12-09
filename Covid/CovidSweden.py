#!/usr/bin/env python3 

import requests
import csv
import datetime

now = datetime.datetime.now()
newCases = 0

r = requests.get("https://opendata.ecdc.europa.eu/covid19/casedistribution/csv", stream=True)

def textStream(r):
    for line in r.raw:
        yield line.decode("utf-8")[:-1]


for l in csv.reader(textStream(r)):
    if l[8] != "SWE":
        continue
    date = datetime.datetime.strptime(l[0], '%d/%m/%Y')
    if now - date <= datetime.timedelta(days=8):
        newCases += int(l[4]) * 100000 / int(l[9])

print("%d neue Fälle" % (newCases))
