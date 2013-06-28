#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 1680x1050 "spannen" vs 3360x1050 "einfach"  """

from BeautifulSoup import BeautifulSoup as BS
import urllib2
import argparse
from tempfile import NamedTemporaryFile
from subprocess import call
from os import rename, path, popen3

useragent = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.14) Gecko/20080418 Ubuntu/7.10 (gutsy) Firefox/2.0.0.14'


def parseArguments():
    fi, fo, fe = popen3('xdpyinfo  | grep dimensions | tr -s " " "\t" | cut -f3')
    defaultResolution = fo.read()[:-1]
    parser = argparse.ArgumentParser(description='Change desktop wallpaper from http://interfacelift.com')
    parser.add_argument('-d', '--only-download', default=False, action='store_true', help='Only download wallpaper')
    parser.add_argument('-k', '--desktop', default="Auto", nargs=1, help='Select the desktop environment')
    # parser.add_argument('resolution', default='16:10', nargs='?', help='Specify resolution')
    parser.add_argument('resolution', default=defaultResolution, nargs='?', help='Specify resolution')
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
    file.write(str(counter))
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
        found.abw = abs(self.x-float(found.x)/found.size) * abs(self.y-float(found.y)/found.size)
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
    opener = urllib2.build_opener()
    while True:
        optimum = opt(ratio.split(':'))
        counter += 1
        request = urllib2.Request('http://interfacelift.com/wallpaper/details/%d/' % counter)
        request.add_header('User-Agent', useragent)
        try:
            connection = opener.open(request)
        except urllib2.HTTPError:
            continue
        page = BS(connection)
        selectForm = page.find('select', 'select')
        if selectForm is None:
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
    preview = page.find('div', 'preview')  # globale Variable
    image = preview.find('a').find('img')
    image_name = image['src'].split('/')[-1]
    return image_name.split('_')[-1].split('.')[0]


def download(url):
    file = NamedTemporaryFile(delete=False)
    request = urllib2.Request(url)
    request.add_header('User-Agent', useragent)
    v = urllib2.build_opener().open(request).read()
    writtenbytes = len(v)
    file.write(v)
    file.close()
    return file.name, writtenbytes


def whichDesktop():  # zur Zeit gnome2, mate und mate16
    isMate = path.isfile('/usr/bin/mateconftool-2')
    isMate16 = path.isfile('/usr/bin/gsettings')
    isGnome = path.isfile('/usr/bin/gconftool-2')
    if isMate16:
        return 'mate16'
    if isMate:
        return 'mate'
    if isGnome:
        return 'gnome2'
    return False

counterFile = '/home/ber/bin/wallpaper'
counter = getCounter(counterFile)
downloadPath = '/home/ber/Desktop/'

args = parseArguments()
size = 0

desktopDependent = {
    'mate16': [
        '/usr/bin/gsettings',
        'set',
        'org.mate.background',
        'picture-filename',
        '%s'
    ],
    'mate': [
        '/usr/bin/mateconftool-2',
        '-s',
        '/desktop/mate/background/picture_filename',
        '--type=string',
        '%s'
    ],
    'gnome2': [
        '/usr/bin/gconftool-2',
        '-s',
        '/desktop/gnome/background/picture_filename'
        '--type=string',
        '%s'
    ]
}
if args.desktop == 'Auto':
    desktop = whichDesktop()
else:
    desktop = args.desktop
command = ' '.join(desktopDependent[desktop])

while size < 50*1024:
    if args.resolution.find(':') == -1:
        optimalResolution('1:1')
        resolution = args.resolution
    else:
        resolution = optimalResolution(args.resolution)
    imageName = '%05d_%s_%s.jpg' % (counter, imageBaseName(), resolution)
    fileName, size = download('http://interfacelift.com/wallpaper/7yz4ma1/' + imageName)
setCounter(counter, counterFile)

if args.only_download:
    rename(fileName, downloadPath + imageName)
else:
    call((command % (fileName)).split())
