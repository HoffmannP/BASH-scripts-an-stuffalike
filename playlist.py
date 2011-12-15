#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, string, xml.parsers.expat, xml.dom.minidom as html, re, sys, time, sqlite3

url = "http://www.antennethueringen.de/at_www/musik/playlist/index.php"
station = "Antenne Thüringen"
dbLocation = "/home/ber/bin/songs.sqlite3"

now = time.localtime()
param = urllib.urlencode({'Tag': 1, 'Stunden': now.tm_hour, 'Minuten': now.tm_min, "Absenden": "Absenden"})
con = urllib.urlopen(url, param)
page = con.read()
con.close()
print "page loaded"

page = re.sub(r'<((?:col|meta|input|img) [^>]*[^/]\s*)>', r'<\1/>', page, flags=re.IGNORECASE)
page = re.sub(r'<([^>]*)checked([^>]*)>', r'<\1checked="checked"\2>', page)
page = re.sub(r'(<script[^>]*>).*?(</script>)', r'\1\2', page, flags=re.DOTALL)
page = re.sub(r'<([^>]*)border=0([^>]*)>', r'<\1border="0"\2>', page)
def decomment(m):
    return m.group(1) + m.group(3).replace("-", "") + m.group(5)
page = re.sub(r'(<!--)(-*)([^>]*)(-*)(-->)', decomment, page)

def urlize(m):
    return m.group(1) + urllib.quote(m.group(2).replace("+", " ")) + m.group(3)
# clean URL for musicload
page = re.sub('(<a class=\'musikkaufen_musicload\' href=\'http://)(.*?)(\' target=\'_blank\'>)', urlize, page)
# clean URL for amazon
page = re.sub('(<a class=\'musikkaufen_amazon\' href=\'http://)(.*?)(\' target=\'_blank\'>)', urlize, page)

page = re.sub(r'</we:master>', '', page)

try:
    document = html.parseString(page)
    print "done parsing"
except xml.parsers.expat.ExpatError as e:
    lines = page.split("\n")
    print >> sys.stderr, "Error: %s (line %d, column %d)" % (xml.parsers.expat.ErrorString(e.code), e.lineno, e.offset)
    width = 100
    print >> sys.stderr, "###", lines[e.lineno-1][e.offset-width:e.offset+width], "###"
    sys.exit()

divs = document.getElementsByTagName("div")
songs = []
for div in divs:
    if div.hasAttribute("class") and div.getAttribute("class") == "box-Content-Border":
        songs.append(div)

def sqlCreate(d):
    createElementTable = "CREATE TABLE IF NOT EXISTS `%s` ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'name' TEXT)"
    createPlaylistTable = "CREATE TABLE IF NOT EXISTS `playlist` (%s)"
    for table in ["artist", "title", "station"]:
        d.execute(createElementTable % table)
        db.commit()
        createPlaylistTable = createPlaylistTable % ("'%s' INTEGER, " % table + r'%s', )
    createPlaylistTable = createPlaylistTable % "'stamp' INTEGER"
    d.execute(createPlaylistTable);
    d.commit()

def sqlInsert(db, attribute):
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
    

db = sqlite3.connect(dbLocation)
db.text_factory = str
sqlCreate(db)
for song in songs:
    infos = song.childNodes[1].childNodes
    sqlInsert(db, {
            "artist": infos[0].childNodes[0].firstChild.nodeValue,
            "title":  infos[0].childNodes[1].firstChild.nodeValue[2:],
            "stamp":  time.mktime(time.strptime(
                    "%d "%time.localtime().tm_year + infos[1].childNodes[2].nodeValue,
                    "%Y den %d.%m um %H:%M Uhr"
                    )),
            "station": station
            })
print "songs inserted"