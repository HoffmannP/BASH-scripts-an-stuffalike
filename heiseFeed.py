#!/usr/bin/python
# -*- coding: utf-8 -*-

print "Content-Type: application/rss+atom"
print

import urllib2, BeautifulSoup, cgi

heiseFeed = "http://www.heise.de/newsticker/heise.rdf"
connection = urllib2.urlopen(heiseFeed)
page = connection.read()
dom = BeautifulSoup.BeautifulSoup(page)
items = dom.findAll("item")
num = 20
for item in items[:num]:
    titleTag = item.find("title")
    url   = "/".join(item.contents[4].split("/")[0:-2])
    page = urllib2.urlopen(url)
    document = BeautifulSoup.BeautifulSoup(page)
    meldung = document.find("div", "meldung_wrapper")
    tags = meldung.contents
    extracts = meldung.findAll(text=lambda text:isinstance(text, BeautifulSoup.Comment))
    extracts[len(extracts):] = meldung.findAll(["script", "noscript"])
    extracts[len(extracts):] = meldung.findAll(["span", "div"], "ISI_IGNORE")
    extracts[len(extracts):] = meldung.findAll("br", "clear")
    [extract.extract() for extract in extracts]
    newItem = BeautifulSoup.Tag(dom, "item")
    newItem.insert(0, titleTag)
    newItem.insert(1, "<link>" + url + "</link>")
    descrTag = BeautifulSoup.Tag(dom, "description")
    descrTag.insert(0, meldung)
    newItem.insert(2, descrTag)
    item.replaceWith(newItem)

[extract.extract() for extract in items[20:]]
images = dom.findAll("img")
for image in images:
    src = image['src'].split("/")
    if src[0] == "":
        image['src'] = "http://www.heise.de" + "/".join(src)
anchors = dom.findAll("a")
for anchor in anchors:
    href = anchor['href'].split("/")
    if href[0] == "":
        anchor['href'] = "http://www.heise.de" + "/".join(href)
print dom.prettify()
