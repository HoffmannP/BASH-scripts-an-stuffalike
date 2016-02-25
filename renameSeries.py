#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import re
import requests

class NoInformationFoundException(Exception):
    def __init__(self, filename, text):
        self.filename = filename
        self.text = text

    def __str__(self):
        return repr(self.filename, self.text)

class Folge(object):
    __reFinden = [
        re.compile('(?P<Name>.*)S(?P<Staffel>\d+)E(?P<Folge>\d+)')]
    __serienWikiSeite = {
        'chicago pd': 'Chicago_P.D.',
        'chicago fire': 'Chicago_Fire',
        'chicago med': 'Chicago_Med',
        'the x files': 'The_X-Files',
        'community': 'Community',
        'shaun the sheep': 'Shaun_the_Sheep',
    }
    __getSectionInfo = 'https://en.wikipedia.org/w/api.php?action=parse&format=json&page=%s&prop=sections'
    __getSection = 'https://en.wikipedia.org/w/api.php?action=parse&format=json&page=%s&section=%d&prop=wikitext'

    def __init__(self, dateiname):
        self.dateiname = dateiname
        self.__matcher()
        self.getName()
        self.getStaffel()
        self.getFolge()
        self.getWikiPage()
        self.getStaffelAbschnitt()

    def __matcher(self):
        print self.dateiname
        for finder in Folge.__reFinden:
            self.match = finder.search(self.dateiname)
            if self.match is not None:
                break;
        if self.match is None:
            raise NoInformationFoundException(self.dateiname, "Can't match season/episode")

    def getName(self):
        self.name = self.match.group('Name').replace('.', ' ').strip()

    def getStaffel(self):
        self.staffel = int(self.match.group('Staffel'))

    def getFolge(self):
        self.folge = int(self.match.group('Folge'))

    def getWikiPage(self):
        self.wikipage = 'List_of_' + Folge.__serienWikiSeite[self.name.lower()] + '_episodes'

    def getFolgenName(self):
        pass

    def getStaffelAbschnitt(self):
        print Folge.__getSection % (self.wikipage, self.getStaffelAbschnittIndex())
        req = requests.get(Folge.__getSection % (self.wikipage, self.getStaffelAbschnittIndex()))
        sect = req.json()['parse']['wikitext']
        # print sect

    def getStaffelAbschnittIndex(self):
        req = requests.get(Folge.__getSectionInfo % self.wikipage)
        sections = req.json()['parse']['sections']
        for section in sections:
            if section['line'] == 'Episodes':
                return int(self.getStaffelUnterabschnittIndex(sections, section['number']))
        raise NoInformationFoundException(self.dateiname, "Can't find episode Section")

    def getStaffelUnterabschnittIndex(self, subsections, sectionNumber):
        for subsection in subsections:
            if subsection['number'][:len(sectionNumber) + 1] == sectionNumber + '.':
                if (' %d ' % self.staffel) in subsection['line']:
                    return subsection['index']
        raise NoInformationFoundException(self.dateiname, "Can't find season")

    def getUnifiedName(self):
        pass

    def unifyName(self):
        pass

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        try:
            folge = Folge(arg)
            folge.unifyName()
        except NoInformationFoundException:
            continue

