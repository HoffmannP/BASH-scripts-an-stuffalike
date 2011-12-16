#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, string, xml.parsers.expat, xml.dom.minidom as html, re, sys, time, sqlite3

url = "http://www.antennethueringen.de/at_www/musik/playlist/index.php"
station = "Antenne Thüringen"
dbLocation = "/home/ber/.songs.sqlite3"

def loadPage():
    now = time.localtime()
    param = urllib.urlencode({'Tag': 1, 'Stunden': now.tm_hour, 'Minuten': now.tm_min, "Absenden": "Absenden"})
    con = urllib.urlopen(url, param)
    page = con.read()
    con.close()
    # print "page loaded"
    return page

def cleanPage(page):
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
        # print "done parsing"
    except xml.parsers.expat.ExpatError as e:
        lines = page.split("\n")
        print >> sys.stderr, "Error: %s (line %d, column %d)" % (xml.parsers.expat.ErrorString(e.code), e.lineno, e.offset)
        width = 200
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
    sA = {}
    sqlParams = []
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
        sA[table] = row[0]
        insertPlaylist = insertPlaylist % ("`%s`, " % table + r'%s', r'?, %s')
        sqlParams.append(sA[table])
    insertPlaylist = insertPlaylist % ("`stamp`", '?')
    sqlParams.append(attribute['stamp'])
    d.execute(searchPlaylist, (attribute['stamp'], sA['station']))
    if d.fetchone() == None:
        d.execute(insertPlaylist, sqlParams)
        db.commit()

document = cleanPage(loadPage())
songs = filter(
    lambda el: el.hasAttribute("class") and el.getAttribute("class") == "box-Content-Border",
    document.getElementsByTagName("div")
    )
insertASong = lambda val: insertSong(val, station, createDB(dbLocation))
for song in songs:
    insertASong(song.childNodes[1].childNodes)
# print "songs inserted"
