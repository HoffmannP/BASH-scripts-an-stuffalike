#!/usr/bin/python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup as BS
import urllib2
import argparse
import htmlentitydefs
import re

useragent = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.14) Gecko/20080418 Ubuntu/7.10 (gutsy) Firefox/2.0.0.14'

def parseArguments():
	parser = argparse.ArgumentParser(description='Video von Mediathek runterladen')
	parser.add_argument('url', nargs=1, help='url der Sendungsseite')
	return parser.parse_args()

url = parseArguments().url

def capitalize(string):
	return (' ').join(part[0].upper() + part[1:] for part in string.split(' '))

def ard(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent', useragent)
	connection = urllib2.build_opener().open(request)
	script = BS(connection).find('div', 'mt-player_container').contents[1].string
	baseURL = "rtmp://vod.daserste.de/ardfs/";
	regEx = re.compile('mediaCollection\.addMediaStream\(0, [0-9]+, "%s", "(.*for=Web-L.*)", "default"\);' % baseURL)
	videoURL = baseURL + regEx.findall(script)[0].split('?')[0]
	videoURL = re.sub('/[^:/]*:videoportal/', '/', videoURL)
	return videoURL

if (url.find('http://') == -1):
	url = urllib2.urlopen('http://www.ardmediathek.de/das-erste/?documentId=%d' % int(url)).geturl()

if (url.find('http://www.ardmediathek.de') > -1):
	outfile = 'ARD - ' + capitalize(url.split('/')[5].split('?')[0].replace('-', ' ')) + '.mp4'
	inurl = ard(url)
	print 'mplayer -dumpstream %s -dumpfile "%s"' % (inurl, outfile)
