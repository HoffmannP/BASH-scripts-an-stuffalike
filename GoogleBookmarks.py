#!/usr/bin/python

def buildTree(bookmarks):
    tree = []
    groups = {}
    for bookmark in bookmarks:
        if bookmark["fold"] == "" or len(bookmark["fold"]) == 0:
            tree.append(bookmark)
        else:
            group = bookmark["fold"][0].encode("utf8")
            if (bookmark["fold"]) > 1:
                bookmark["fold"] = bookmark["fold"][1:]
            else:
                bookmark["fold"] = ""
            if groups.has_key(group):
                groups[group].append(bookmark)
            else:
                groups[group] = [bookmark]
    for name, group in groups.iteritems():
        tree.append({"name": name, "tree": buildTree(group)})
    return tree

def htmlizeTree(tree, base):
    from BeautifulSoup import Tag, NavigableString
    import cgi
    elements = []
    for branch in tree:
        if branch.has_key("href"):
            el = Tag(base, "A")
            for attrib in ("href", "add_date", "icon"):
                el[attrib] = branch[attrib]
        else:
            el = Tag(base, "H3")
        try:
            el.insert(0, NavigableString(branch["name"]))
        except:
            el.insert(0, NavigableString("[can not convert]"))
            print "can not convert ", branch["name"]
        dt = Tag(base, "DT")
        dt.insert(0, el)
        elements.append(dt)
        if branch.has_key("tree"):
            elements.append(htmlizeTree(branch["tree"], base))
    dl = Tag(base, "DL")
    for i, element in enumerate(elements):
        dl.insert(i, element)
    dd = Tag(base, "DD")
    dd.insert(0, dl)
    return dd

def writeBookmarks(filename, bookmarks):
    from BeautifulSoup import BeautifulSoup
    for bookmark in bookmarks:
        bookmark["fold"] = bookmark["fold"].split("/")
        if bookmark["fold"][0] == "Andere Lesezeichen":
            bookmark["fold"] = bookmark["fold"][1:]
    tree = buildTree(bookmarks)
    page = BeautifulSoup()
    bookmarkFile = open(filename, "w")
    bookmarkFile.write('''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>''')
    dd = htmlizeTree(tree, page)
    bookmarkFile.write(dd.prettify())
    bookmarkFile.close()

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
        names += (name.contents[0], )
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
        folder = getParentName(bookmark.parent)
        if len(folder) == 0 or folder[0] != "Lesezeichenleiste":
            folder = ("Andere Lesezeichen",) + folder
        bms.append({
                "name": getContent(bookmark, 0),
                "href": getAttribute(bookmark, "href"),
                "fold": "/".join(folder),
                "add_date": getAttribute(bookmark, "add_date"),
                "icon": getAttribute(bookmark, "icon"),
                "srce": filename
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
    bookmarks.sort(key=lambda x: x["href"])
    groups = gruppiere(cleanDoubles(bookmarks))
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

def clearBookmarks(filename):
    from BeautifulSoup import BeautifulSoup
    page = open(filename, "r")
    struct = BeautifulSoup(page)
    page.close()
    As = struct.findAll("a")
    for A in As:
        A["href"] = ""
        A["icon"] = ""
    page = open(filename + ".new", "w")
    page.write(struct.prettify())
    page.close()

def main():
    divs    = ("Arbeit", "Katja", "Paula", "Katja neu")
    header  = ["name", "href", "fold", "add_date", "icon", "srce"]
    fn_base = "/home/ber/Dropbox/Lesezeichen %s"
    fn_in   = lambda i: fn_base % ("auf %s.html" % i)
    fn_out  = lambda i: fn_base % ("auf %s.csv"  % i)
    bms = []
    for div in divs:
        bm = extractBookmarks(fn_in(div))
        csvWrite(fn_out(div), bm, header)
        bms += bm
    bms = filter(cleanNonsense, bms)
    bms = merge(bms)
    writeBookmarks(fn_base % "global.html", bms)
    csvWrite(fn_base % "global.csv", bms, header)

main()
