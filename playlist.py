#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, urllib, time, urllib2, BeautifulSoup, sqlite3

dbLocation = '/home/ber/.songs.sqlite3'

class abstractRadio:
    name = None
    url  = None
    def params(self, hour, min):
        raise NotImplementedError
    def filterSongs(self, document):
        raise NotImplementedError

class AntenneThueringen(abstractRadio):
    name = u'Antenne Thüringen'
    url  = 'http://www.antennethueringen.de/at_www/musik/playlist/index.php'
    def params(self, hour, min):
        return {'Tag': 1, 'Stunden': hour, 'Minuten': min, "Absenden": "Absenden"}
    def filterSongs(self, document):
        songTags = document.findAll('div', {"class": "box-Content-Border"})
        songs = []
        for songTag in songTags:
            songInfo = songTag.contents[1].contents
            songs.append({
                    "artist": songInfo[0].contents[0].contents[0],
                    "title":  songInfo[0].contents[1].contents[0][3:],
                    "stamp":  time.mktime(time.strptime(
                            "%d "%time.localtime().tm_year + songInfo[1].contents[2][1:],
                            "%Y den %d.%m um %H:%M Uhr"
                            )),
                    "station": self.name
                    })
        return songs

class LandesWelle(abstractRadio):
    name = u'LandesWelle Thüringen'
    url  = 'http://www.landeswelle.de/lwt/playlist/index.html'
    def params(self, hour, min):
        return {'search[date]': int(time.time()), 'search[hour]': hour, 'search[minute]': min}
    def filterSongs(self, document):
        songTags = document.findAll('div', {"class": "box "})
        songs = []
        for songTag in songTags:
            songInfo = songTag.contents[3].contents
            songs.append({
                    "artist": songInfo[3].contents[0][1:-1].upper(),
                    "title":  songInfo[5].contents[0][1:-1].upper(),
                    "stamp":  time.mktime(time.strptime(
                            songInfo[1].contents[0],
                            "%d.%m.%Y %H:%M Uhr"
                            )),
                    "station": self.name
                    })
        return songs
        
def genParams(Radio, playlisttime):
    if playlisttime == None: 
        today = time.localtime(time.time() - 10*60)
        hour = today.tm_hour
        min = today.tm_min
    else:
        hour, min = playlisttime.split(":")
    return Radio.params(hour, min)

def parseArguments(listStations):
    parser = argparse.ArgumentParser(description='Grab a list of songs aired recently and import them into a sqlite3-DB')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='show verbose output')
    parser.add_argument('radio', choices=listStations, type=str,               help='querry the selected radiostation')
    parser.add_argument('-t', '--time',                type=str,               help='grab list of songs aired at this time')
    parser.add_argument('-p', '--page',    default=False, action='store_true', help='print pretty version downloaded HTML document')
    return parser.parse_args()

def getDocument(Radio, Arguments):
    postData = urllib.urlencode(genParams(Radio, Arguments.time))
    connection = urllib2.urlopen(Radio.url, postData)
    if Arguments.verbose:
        print "Requesting %s (POST-Data: %s)" % (Radio.url, postData)
    page = connection.read().decode('iso-8859-15', 'ignore').encode('utf-8')
    connection.close()
    if Arguments.verbose:
        print "page loaded"
    document = BeautifulSoup.BeautifulSoup(page, convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES)
    if Arguments.page:
        print document.prettify()
    if Arguments.verbose:
        print "done parsing"
    return document

def createDB(db_URI):
    db = sqlite3.connect(db_URI)
    db.text_factory = str
    createElementTable = "CREATE TABLE IF NOT EXISTS `%s` ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'name' TEXT)"
    createPlaylistTable = "CREATE TABLE IF NOT EXISTS `playlist` (%s)"
    for table in ["artist", "title", "station"]:
        db.execute(createElementTable % table)
        db.commit()
        createPlaylistTable = createPlaylistTable % ("'%s' INTEGER, " % table + r'%s', )
    createPlaylistTable = createPlaylistTable % "'stamp' INTEGER"
    db.execute(createPlaylistTable)
    db.commit()
    return db

def insertSong(attribute, Radio, db):
    d = db.cursor()
    searchElement = "SELECT `id` FROM `%s` WHERE `name` = ?"
    insertElement = "INSERT INTO `%s` (`name`) VALUES (?)"
    searchPlaylist = "SELECT `stamp` FROM `playlist` WHERE `stamp` = ? AND `station` = ?"
    insertPlaylist = "INSERT INTO `playlist` (%s) VALUES (%s)"
    for table in ["artist", "title", "station"]:
        d.execute(searchElement % table, [attribute[table]])
        row = d.fetchone()
        if row == None:
            d.execute(insertElement % table, [attribute[table]])
            db.commit()
            d.execute(searchElement % table, [attribute[table]])
            row = d.fetchone()
        attribute[table] = row[0]
        insertPlaylist = insertPlaylist % ("`%s`, " % table + r'%s', r'?, %s')
    insertPlaylist = insertPlaylist % ("`stamp`", '?')
    d.execute(searchPlaylist, (attribute['stamp'], attribute['station']))
    if d.fetchone() == None:
        d.execute(insertPlaylist, [attribute["artist"], attribute["title"], attribute["station"], attribute['stamp']])
        db.commit()

def main():
    stations = {
        'AntenneThueringen': AntenneThueringen,
        'LandesWelle': LandesWelle
        }
    args = parseArguments(stations.keys())
    radio = stations[args.radio]()
    document = getDocument(radio, args)
    songs = radio.filterSongs(document)
    def insertASong(val):
        if args.verbose:
            print val["artist"] + " - " + val["title"] + " @" + str(val["stamp"])
        insertSong(val, radio, createDB(dbLocation))
    for song in songs:
        insertASong(song)
    if args.verbose:
        print "songs inserted"

main()
