#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs4
from requests import get, put, post, cookies
from random import randint as rnd
from subprocess import call
from json import loads as json_parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib3 import disable_warnings as urllib3_disable_warnings, exceptions as urllib3_exceptions
urllib3_disable_warnings(urllib3_exceptions.InsecureRequestWarning)

resolution = '1920x1080' # zwei Monitore á 1920x1080
category = 'Nature'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.75 Chrome/62.0.3202.75 Safari/537.36'
clickshare_host = '192.168.2.1'
clickshare_password = 'integrator'

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
	with open(filename, 'w') as f:
		f.buffer.write(browser.raw(uri))

def clickshare(target, value=None):
	url = f'https://{clickshare_host}:4001/{target}'
	if value is None:
		response = get(url,
		auth=('integrator', clickshare_password),
		verify=False)
		return json_parse(response.text)['data']['value']
	else:
		response = put(url,
		{'value': value},
		auth=('integrator', clickshare_password),
		verify=False)
		return json_parse(response.text)['message']
	if response.status_code != 200:
		raise Exception(json_parse(response.text)['message'])
	return json_parse(response.text)

class ServeFile(BaseHTTPRequestHandler):
	filename = ''
	def do_GET(self):
		self.send_response(200)
		self.send_header("Content-Type", "image/jpg")
		self.end_headers()
		with open(self.filename, 'rb') as f:
			self.wfile.write(f.read())

def setWallpaper(filename):
	clickshare('v1.2/Wallpapers/UpLoadUrl', 'http://192.168.2.207:4001/wallpaper.jpg')
	ServeFile.filename = filename
	with HTTPServer(("", 4001), ServeFile) as httpd:
		httpd.handle_request()
		print('Start Upload')
		print(clickshare('v1.2/Wallpapers/UpLoadSetStart', 'true'))
	newestId = clickshare('v1.2/Wallpapers/UserWallpapers/WallpapersNumber')
	newestWallpapername = clickshare(f'v1.2/Wallpapers/UserWallpapers/WallpapersTables/{newestId}/Filename')
	clickshare('v1.2/Wallpapers/CurrentWallpaper', newestWallpapername)


if __name__ == '__main__':
	# wallpaperSite = WallpapersWide(resolution, category)
	# imageInfo = wallpaperSite.randomImage()
	# localImageFile = '/tmp/wallpaper-' + imageInfo['identifier'] + '.jpg'
	# download(imageInfo['url'], localImageFile)
	localImageFile = '/tmp/wallpaper-trees_are_green.jpg'
	setWallpaper(localImageFile)
