#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, urllib, urllib2, string, xml.parsers.expat, xml.dom.minidom as html, re, sys, time, sqlite3

url = 'http://www.antennethueringen.de/at_www/musik/playlist/index.php'
station = 'Antenne Thüringen'
dbLocation = '/home/ber/.songs.sqlite3'

def cargs():
    parser = argparse.ArgumentParser('Grab a list of songs aired recently and import them into a sqlite3-DB')
    parser.add_argument('--time', '-t', type=str, help='Time for which you like to get the playlist')
    parser.add_argument('--verbose', '-v', action='store_true', default=False, help='Some status output')
    parser.add_argument('--page', '-p', action='store_true', default=False, help='Print page after download')
    parser.add_argument('--width', type=int, default=30, help='Number of chars printed around parsing error')
    return parser.parse_args()

def loadPage(songtime, verbose, printPage):
    if songtime == None: 
        now = time.localtime()
        hour = now.tm_hour
        min = now.tm_min
    else:
        hour, min = songtime.split(":")
    param = urllib.urlencode({'Tag': 1, 'Stunden': hour, 'Minuten': min, "Absenden": "Absenden"})
    con = urllib2.urlopen(url, param)
    page = con.read().decode('iso-8859-15', 'ignore').encode('utf-8')
    if printPage:
        print page
    con.close()
    if verbose:
        print "page loaded"
    return page

def cleanPage(page, verbose, width):
    page = re.compile(r'<((?:col|meta|input|img) [^>]*[^/]\s*)>', re.IGNORECASE).sub(r'<\1/>', page)
    page = re.compile(r'<([^>]*)checked([^>]*)>').sub(r'<\1checked="checked"\2>', page)
    page = re.compile(r'(<script[^>]*>).*?(</script>)', re.DOTALL).sub(r'\1\2', page)
    page = re.compile(r'<([^>]*)border=0([^>]*)>').sub(r'<\1border="0"\2>', page)
    def decomment(m):
        return m.group(1) + m.group(3).replace("-", "") + m.group(5)
    page = re.sub(r'(<!--)(-*)([^>]*)(-*)(-->)', decomment, page)

    def urlize(m):
        return m.group(1) + urllib.quote(m.group(2).replace("+", " ")) + m.group(3)
    # clean URL for musicload
    page = re.compile('(<a class=\'musikkaufen_musicload\' href=\'http://)(.*?)(\' target=\'_blank\'>)').sub(urlize, page)
    # clean URL for amazon
    page = re.compile('(<a class=\'musikkaufen_amazon\' href=\'http://)(.*?)(\' target=\'_blank\'>)').sub(urlize, page)
    def clearTag(m):
        return m.group(1) + urllib.quote(m.group(2)) + m.group(3) + urllib.quote(m.group(4)) + m.group(5)
    # clean ALT and TITLE artist tag
    page = re.compile('(<img src=\'[^\']*?\' border="0" title=\')(.*?)(\' alt=\')(.*?)(\' style=\'.*?\'>)').sub(clearTag, page)

    page = re.compile(r'</we:master>').sub('', page)

    try:
        document = html.parseString(page)
        if verbose:
            print "done parsing"
    except xml.parsers.expat.ExpatError as e:
        lines = page.split("\n")
        print >> sys.stderr, "Error: %s (line %d, column %d)" % (xml.parsers.expat.ErrorString(e.code), e.lineno, e.offset)
        print >> sys.stderr, "###", lines[e.lineno-1][e.offset-width:e.offset+width], "###"
        sys.exit()
    
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
    db.execute(createPlaylistTable);
    db.commit()
    return db

def insertSong(songInfo, station, db):
    attribute = {
        "artist": songInfo[0].childNodes[0].firstChild.nodeValue,
        "title":  songInfo[0].childNodes[1].firstChild.nodeValue[2:],
        "stamp":  time.mktime(time.strptime(
                "%d "%time.localtime().tm_year + songInfo[1].childNodes[2].nodeValue,
                "%Y den %d.%m um %H:%M Uhr"
                )),
        "station": station
        }
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
        d.execute(insertPlaylist, [v for k,v in attribute.iteritems()])
        db.commit()

args = cargs()
document = cleanPage(loadPage(args.time, args.verbose, args.page), args.verbose, args.width)
songs = filter(
    lambda el: el.hasAttribute("class") and el.getAttribute("class") == "box-Content-Border",
    document.getElementsByTagName("div")
    )
insertASong = lambda val: insertSong(val, station, createDB(dbLocation))
for song in songs:
    insertASong(song.childNodes[1].childNodes)
if args.verbose:
    print "songs inserted"
