#!/usr/bin/python

def getParentName(p):
    p = p.parent
    if p is None or p.name == u'document':
        return ()
    while p.name != "dt":
        p = p.parent
        if p is None or p.name == u'document':
            return ()
    names = getParentName(p)
    name = p.find("h3")
    if name is not None:
        names = (name.contents[0], ) + names
    return names

def getAttribute(self, attribute):
    if self.has_key(attribute):
        return self[attribute]
    else:
        return None

def getContent(self, num):
    c = self.contents
    if c is None:
        return ""
    if len(c) <= num:
        return ""
    return c[num]

def extractBookmarks(filename):
    bms = []
    bookmarkfile = open(filename, "r")
    from BeautifulSoup import BeautifulSoup
    for bookmark in BeautifulSoup(bookmarkfile).findAll("a"):
        bms.append({
                "name": getContent(bookmark, 0),
                "href": getAttribute(bookmark, "href"),
                "fold": "/".join(getParentName(bookmark.parent)),
                "date": getAttribute(bookmark, "add_date"),
                "icon": getAttribute(bookmark, "icon"),
                })
    bookmarkfile.close()
    return bms
        
def values(self, keys):
    v = []
    for key in keys:
        v.append(self[key])
    return v

def csvWrite(filename, bookmarks, header):
    import csv
    csvfile = open(filename, "wb")
    csv = csv.writer(csvfile, delimiter=";")
    csv.writerow(header)
    for bookmark in bookmarks:
        csv.writerow(values(bookmark, header))
    csvfile.close()

def cleanDoubles(bookmarks):
    old = bookmarks[0]
    new = [bookmarks[0]]
    conflicts = []
    for bookmark in bookmarks[1:]:
        if bookmark["href"] != old["href"] or bookmark["name"] != old["name"] or bookmark["fold"] != old["fold"]:
            new.append(bookmark)
            old = bookmark
        else:
            if old["icon"] is None and bookmark["icon"] is not None:
                new = new[:-1]
                old["icon"] = bookmark["icon"]
                new.append(old)
    return new

def extractDifferentAttributes(attribName, bookmarks):
    attributes = [bookmarks[0][attribName]]
    for bookmark in bookmarks[1:]:
        new = True
        for attribute in attributes:
            if bookmark[attribName] == attribute:
                new = False 
        if new:
            attributes.append(bookmark[attribName])
    return attributes

def gruppiere(bookmarks):
    groups = [[bookmarks[0]]]
    for bookmark in bookmarks[1:]:
        if bookmark["href"] == groups[-1][0]["href"]:
            groups[-1].append(bookmark)
        else:
            groups.append([bookmark])
    return groups
            
def nachfrage(auswahl, name):
    for i, wahl in enumerate(auswahl):
        print "%d) %s" % (i+1, wahl)
    print "%d) [new entry]" % (i+2)
    d = try_int(raw_input("Select a %s for that bookmark: " % name))
    while d is None or d < 1 or d > i+2:
        d = try_int(raw_input("Select a %s for that bookmark: " % name))
    if d == i+2:
        return raw_input("Enter new %s for that bookmark: " % name)
    else:
        return auswahl[i-1]

def merge(bookmarks):
    groups = gruppiere(bookmarks)
    bookmarks = []
    for group in groups:
        if len(group) > 1:
            print "\nBookmark linking to %s (one name: %s)" % (group[0]["href"], group[0]["name"])
            for attribName in ["name", "fold"]:
                attribute = extractDifferentAttributes(attribName, group)
                if len(attribute) > 1:
                    attribute = [nachfrage(attribute, attribName)]
                group[0][attribName] = attribute[0]
        bookmarks.append(group[0])
    return bookmarks

def cleanNonsense(bookmark):
    if bookmark["href"] is None:
        return False
    if bookmark["href"][0:len("http://")] == "http://" or \
    bookmark["href"][0:len("https://")] == "https://" or \
    bookmark["href"][0:len("javascript:")] == "javascript:":
        return True

def try_int(string):
    try:
        return int(string)
    except ValueError:
        return None

def main():
    divs    = ("Arbeit", "Katja", "Paula", "Katja neu")
    header  = ["name", "href", "fold", "date", "icon"]
    fn_base = "/home/ber/Dropbox/Lesezeichen %s"
    fn_in   = lambda i: fn_base % ("auf %s.html" % i)
    fn_out  = lambda i: fn_base % ("auf %s.csv"  % i)
    bms = []
    for div in divs:
        bm = extractBookmarks(fn_in(div))
        csvWrite(fn_out(div), bm, header)
        bms += bm
    bms = filter(cleanNonsense, bms)
    bms.sort(key=lambda x: x["href"])
    bms = cleanDoubles(bms)
    bms = merge(bms)
    csvWrite(fn_base % "global.csv", bms, header)
    

main()
