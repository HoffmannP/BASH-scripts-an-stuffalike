#!/usr/bin/env python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
from requests import post, get
from urlparse import urlparse, urlunparse, parse_qs
from base64 import b64decode, b64encode
# user = kanga2402
# pass = 24022014

def download(id):
    print id,
    url = "http://www.portraitbox.com/galleries/ebenbild/index.php?page=showpicture&id=%08d&album_id=343100" % id
    payload = {
        'getimageview' :    1,
        'leftOpen' :        0,
        'rightOpen':        0
    }
    cookies = {
        'PHPSESSID':    '7fa50c04c9d69efa072751f24ba17860'
    }
    request = post(url, data=payload, cookies=cookies)
    page = BeautifulSoup(request.text)
    images = page.select('a.MagicZoomPlus img')
    if len(images) == 0:
        print "Nicht vorhanden"
        return
    oldImageUrl = images[2]['src']
    parts = urlparse(oldImageUrl)
    hashOld = b64decode(parse_qs(parts[4])['hash'][0])
    hashParts = hashOld.split('#')
    # 0, 1 => Bildidentify
    # 2 => size (1500, 500, 400, 300, 220, 150, 50)
    # 3 => effect (1 normal, 2 s/w, 3 sepia)
    # 4 => show Bar?
    # 5 => position (top, middle, bottom)
    # 6 => lightness of text
    # 7 => stripes (0 no, 1 diag, 2 circle, 3 grid, 4 grid, 5 eng diag)
    # 8 => text
    # 9 => font
    # 10 => barsize
    # 11 => color
    # 12 => background
    hashParts[4] = '0'
    hashParts[2] = '1500'
    hashNew = '#'.join(hashParts)
    parts = (parts[0], parts[1], parts[2], parts[3], "hash=" + b64encode(hashNew), parts[5])
    newImageUrl = urlunparse(parts)
    request = get(newImageUrl, cookies=cookies)
    f = open('Bild_%08d.jpg' % id, 'wb')
    f.write(request.content)
    f.close()
    print "done"

for id in range(22979099,22980820):
    download(id)
