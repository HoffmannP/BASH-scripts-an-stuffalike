#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 1680x1050 "spannen" vs 3360x1050 "einfach"  """

from bs4 import BeautifulSoup as bs4
from requests import get, Session
from random import randint as rnd
from subprocess import call


wallpaperPrefix = '/tmp/wallpaper'
sfx = '.jpg'
baseUrl = 'http://wallpaperswide.com/'
resolution = '1680x1050'
desktop = 'cinnamon'
callSetting = {
    'mate': lambda fn: call(['/usr/bin/gsettings', 'set', 'org.mate.background', 'picture-filename', fn]),
    'cinnamon': lambda fn: call(['/usr/bin/gsettings', 'set', 'org.cinnamon.desktop.background', 'picture-uri', 'file://' + fn])
}

def maxPage():
    request = get(baseUrl + resolution + '-wallpapers-r.html')
    page = bs4(request.text, "lxml")
    return int(page.select('div.pagination a')[5].text)

def imageSelect():
    url = baseUrl + resolution + '-wallpapers-r/page/' + str(rnd(1, maxPage()))
    page = bs4(get(url).text, "lxml")
    return page.select('li.wall div.thumb a')[2*rnd(0, 9)]['href']

def getReferer(url, referer):
    useragent = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.14) Gecko/20080418 Ubuntu/7.10 (gutsy) Firefox/2.0.0.14'
    session = Session()
    session.headers.update({
        'referer': referer,
        'user-agent': useragent
    })
    return session.get(url)

def setWallpaper():
    page = imageSelect()
    urlPage = baseUrl + page
    urlImage = baseUrl + 'download' + page[:-len('s.html')] + '-' + resolution + sfx
    fileName = wallpaperPrefix + str(rnd(0, 1E5)) + sfx
    with open(fileName, 'w') as f:
         f.write(getReferer(urlImage, urlPage).content)
    callSetting[desktop](fileName)

if __name__ == '__main__':
    setWallpaper()
