#!/usr/bin/python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup as BS
from urllib2 import urlopen, HTTPError
import argparse
from tempfile import NamedTemporaryFile
from subprocess import call
from os import rename

def parseArguments():
    parser = argparse.ArgumentParser(description='Change desktop wallpaper from http://interfacelift.com')
    parser.add_argument('-d', '--only-download', default=False, action='store_true', help='Only download wallpaper')
    parser.add_argument('resolution', default='16:10', nargs='?', help='Specify resolution')
    return parser.parse_args()

def getCounter(fn):
    try:
        file = open(fn, 'r')
        c = int(file.read())
        file.close()
    except IOError:
        c = 1
    return c

def setCounter(counter, fn):
    file = open(fn, 'w')
    c = file.write(str(counter))
    file.close()

def mean(a, b):
    return (a+b)/2

class opt:
    abw = 999999
    size = 0
    rX = 1
    rY = 1
    x = 1
    y = 1
    def __init__(self, list):
        self.x, self.y = int(list[0]), int(list[1])
    def find(self, resolution):
        found = opt(resolution)
        found.size = mean(found.x/self.x, found.y/self.y)
        found.abw  = abs(self.x-float(found.x)/found.size) * abs(self.y-float(found.y)/found.size)
        if (found.abw < self.abw) or ((found.abw - self.abw < 1e-05) and (found.size > self.size)):
            self.abw = found.abw
            self.size = found.size
            self.rX = found.x
            self.rY = found.y
    def val(self):
        return '%sx%s' % (self.rX, self.rY) 

# da nicht jede Nummer einem Hintergrundbild entspricht wird
# solange gesucht bis eine Nummber gefunden wird die passt
def optimalResolution(ratio):
    global counter
    global page
    while True:
        optimum = opt(ratio.split(':'))
        counter += 1
        url = 'http://interfacelift.com/wallpaper/details/%d/' % counter
        try:
            connection = urlopen(url)
        except HTTPError:
            continue
        page = BS(connection)
        selectForm = page.find('select', 'select')
        if selectForm == None:
            continue
        options = selectForm.findAll('option')
        for option in options:
            resolution = option['value']
            if resolution is None or resolution == '':
                continue
            optimum.find(resolution.split('x'))
        break
    return optimum.val()

def imageBaseName():
    preview = page.find('div', 'preview')
    image = preview.find('a').find('img')
    image_name = image['src'].split('/')[-1]
    return image_name.split('_')[-1].split('.')[0]
    
def download(url):
    file = NamedTemporaryFile(delete=False)
    v = urlopen(url).read()
    writtenbytes = len(v)
    file.write(v)
    file.close()
    return file.name, writtenbytes

counterFile = '/home/ber/bin/wallpaper'
counter = getCounter(counterFile)
downloadPath = '/home/ber/Desktop/'
# wallpaper_conf_key="/desktop/gnome/background/picture_filename"
wallpaper_conf_key="/desktop/mate/background/picture_filename"
args = parseArguments()
size = 0
while size < 50*1024:
    resolution = optimalResolution(args.resolution)
    imageName = '%05d_%s_%s.jpg' % (counter, imageBaseName(), resolution)
    fileName, size = download('http://interfacelift.com/wallpaper/7yz4ma1/' + imageName)
setCounter(counter, counterFile)

if args.only_download:
    rename(fileName, downloadPath + imageName)
else:
    call([
            '/usr/bin/mateconftool-2', #gconftool-2',
            '-s',
            wallpaper_conf_key,
            '--type=string',
            fileName
        ])

    
