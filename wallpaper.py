#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs4
from requests import get, post, cookies
from random import randint as rnd
from subprocess import call

desktop = 'cinnamon'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.75 Chrome/62.0.3202.75 Safari/537.36'
resolution = '1680x1050'
category = 'Nature'

"""
Ab hier nichts mehr ändern
"""


class Browser:
	def __init__(self, userAgent=USER_AGENT, **kwargs):
		self.jar = cookies.RequestsCookieJar()
		self.header = kwargs
		self.header['user-agent'] = userAgent

	def addCookie(self, name, value):
		self.jar.set(name, value)

	def load(self, response):
		return bs4(response.text, "lxml")

	def get(self, url):
		result = get(url, cookies=self.jar, headers=self.header)
		self.jar.update(result.cookies)
		return self.load(result)

	def post(self, url, data):
		result = post(url, data=data, cookies=self.jar, headers=self.header)
		self.jar.update(result.cookies)
		return self.load(result)

	def raw(self, url):
		return get(url, cookies=self.jar, headers=self.header).content


class WallpapersWide:
	def __init__(self, resolution, category):
		self.domain = 'http://wallpaperswide.com/'
		self.category = category.lower().replace(' ', '_')
		self.resolution = resolution
		self.browser = Browser(referer=self.domain + self.category + '-desktop-wallpapers.html')
		self.setResolution(resolution)

	def setResolution(self, resolution):
		self.browser.addCookie('PHPSESSID', '98b95c900e96141d2501763b834fc10a')
		self.browser.addCookie('rrFilter', '1')
		self.browser.post(
			self.domain + 'setfilter.html', data={'flt_res': resolution})

	def maxPage(self):
		return int(self.browser.get(
			self.domain + self.category + '-desktop-wallpapers.html').select(
			'div.pagination a')[-2].text)

	def getImage(self, link):
		identifier = link.split('/')[1].split('-')[0]
		return {
			'site': self.domain + identifier,
			'url': self.domain + 'download/' + identifier + '-wallpaper-' + self.resolution + '.jpg',
			'identifier': identifier
		}

	def randomImage(self):
		return self.getImage(self.browser.get(
			self.domain + self.category + '-desktop-wallpapers/page/' + str(rnd(1, self.maxPage()))).select(
			'li.wall div.thumb a')[2*rnd(0, 9)]['href'])

def download(uri, filename):
	browser = Browser()
	with open(filename, 'wb') as f:
		f.write(browser.raw(uri))

def buildThreeDisplayWallpaper(original):
	center = original[:-3] + "center.jpg"
	call(["/usr/bin/convert", original, "-gravity", "center", "-crop", "38%x100%", "+repage", center])
	combined = original[:-3] + "3dsp.jpg"
	call(["/usr/bin/convert", original, center, "+append", combined])
	call(["/bin/rm", center])
	return combined

setWallpaperFuncion = {
    'mate': lambda fn: call(['/usr/bin/gsettings', 'set', 'org.mate.background', 'picture-filename', fn]),
    'cinnamon': lambda fn: call(['/usr/bin/gsettings', 'set', 'org.cinnamon.desktop.background', 'picture-uri', 'file://' + fn])}

if __name__ == '__main__':
	wallpaperSite = WallpapersWide(resolution, category)
	imageInfo = wallpaperSite.randomImage()
	localImageFile = '/tmp/wallpaper-' + imageInfo['identifier'] + '.jpg'
	download(imageInfo['url'], localImageFile)
	setWallpaperFuncion[desktop](localImageFile)
