#!/usr/bin/env python
# -*- coding: utf8 -*-

import requests
import re
import os

produkt = 'ProductPage .html'
groesse = 'L'  # confection size or XS/S/M/L/XL
#### No changes below this point ####

if type(groesse) == str:
    groesse = '%02d' % ['XS', 'S', 'M', 'L', 'XL'].index(groesse.upper())
url = 'https://www.tchibo.de/%s' % produkt
email = '%yourEm@il'
mailTemplate = """
echo "Dein Produkt ist in deiner Größe <a href='%s'>verfügbar!</a>" | \
mail -s "Tschibo Produkt verfügbar" "%s"
"""
webrequest = requests.get(url)
reS = re.compile('class="([^"]*dimm%s[^"]*)"' % groesse)
found = reS.search(webrequest.text)
if 'not-available' not in found.group(1).split():
    os.system(mailTemplate % (url, email))
