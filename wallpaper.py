#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 1680x1050 "spannen" vs 3360x1050 "einfach"  """

from subprocess import call
from random import randint as rnd
from bs4 import BeautifulSoup as bs4
from requests import get, Session


WALLPAPER_PREFIX = '/home/ber/.wallpaper'
SFX = '.jpg'
BASE_URL = 'http://wallpaperswide.com'
RESOLUTION = '3840x1080'
DESKTOP = 'cinnamon'
CALL_SETTING = {
    'mate': lambda fn: call([
        '/usr/bin/gsettings',
        'set',
        'org.mate.background',
        'picture-filename',
        fn]),
    'cinnamon': lambda fn: call([
        '/usr/bin/gsettings',
        'set',
        'org.cinnamon.desktop.background',
        'picture-uri',
        'file://' + fn])
}
IGNORED_CATEGORIES = [
    'Aero',
    'Army',
    'Funny',
    'Movies',
    'Models',
    'Girls',
    'Cute',
    'Motors',
    'Celebrities',
    'Games',
    'Sports']

def max_page():
    """ number of current pages """
    request = get(BASE_URL + '/' + RESOLUTION + '-wallpapers-r.html')
    page = bs4(request.text, "lxml")
    return int(page.select('div.pagination a')[1].text)

def image_select():
    """ randomly return a image url """
    url = BASE_URL + '/' + RESOLUTION + '-wallpapers-r/page/' + str(rnd(1, max_page()))
    page = bs4(get(url).text, "lxml")
    return page.select('li.wall div.thumb a')[2*rnd(0, 9)]['href']


def get_referer(url, referer):
    """ creates the referer object """
    useragent = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.14)'+\
    ' Gecko/20080418 Ubuntu/7.10 (gutsy) Firefox/2.0.0.14'
    session = Session()
    session.headers.update({
        'referer': referer,
        'user-agent': useragent
    })
    return session.get(url)


def categorie_ignore(url, ignore_categories):
    """ ignores defined categories of wallappers  """
    page = bs4(get(url).text, "lxml")
    categories = page.select('#content ul')[1].select('a')
    for categorie in categories:
        if categorie.get_text().split('/')[0] in ignore_categories:
            return True
    return False


def set_wallpaper():
    """main function to randomly set the wallpaper without ignored categories"""
    while True:
        page = image_select()
        url_page = BASE_URL + page
        if not categorie_ignore(url_page, IGNORED_CATEGORIES):
            break
    url_image = BASE_URL + '/download' + page[:-len('s.html')] + '-' + RESOLUTION + SFX
    file_name = WALLPAPER_PREFIX + str(rnd(0, 1E5)) + SFX
    with open(file_name, 'w') as fi:
        fi.buffer.write(get_referer(url_image, url_page).content)
    CALL_SETTING[DESKTOP](file_name)


if __name__ == '__main__':
    set_wallpaper()
