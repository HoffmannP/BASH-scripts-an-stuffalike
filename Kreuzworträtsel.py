#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup  # using lxml
import requests
import sys

url = 'http://www.zeit.de/leben/kreuzwortraetsel'
As = BeautifulSoup(requests.get(url, verify=False).text, "lxml").findAll('a')
folder = u'/home/ber/Dokumente/Kreuzworträtsel/'
link = None

for a in As:
    if 'als PDF' in a.text:
        link = a['href']
        break

if link is None:
    print "Nichts gefunden"
    sys.exit(1)

tmp = link.split('/')[-2:]
tmp2 = tmp[1].split('_')
name = '_'.join(tmp2[:-1] + [tmp[0]] + [tmp2[-1]])

# print link
with open(folder + name, 'wb') as f:
    f.write(requests.get(link, verify=False).content)
print name
