#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, BeautifulSoup

urls = [
    {
        server: 1,
        h: '5e5b6ca358329a5f025afa14d7f191db',
        email: 'p2lebe@uni-jena.de'
        },
    {
        server: 2,
        h: '95043ab93c3c9b7f71b3db50ceb05ed3',
        email: 'p2lebe@uni-jena.de'
        }
    ]

baseUrl = 'https://mail%d-thueringen.dfn.de:83/Search?h=%s&email=%s'
UserAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30'

requestShow = {
    action: 'Message:Release',
    screen: 'Search',
    page: none,
    'ignore_escapes:criterion': none,
    pg: none,
    pageSize: 25,
    message_action1: none,
    toggle_msg: 'msg[]',
    message_action2: 'Release'
    }

page = BeautifulSoup.BeautifulSoup(
    urllub2.urlopen(
        baseUrl % urls[0],
        data = urllib.urlencode(requestShow)
        )
    );



def fullTextItem(description, myUrl, aXml):
    global itemsToReplace
    try:
        page = 
            urllib2.urlopen(
                urllib2.Request(
                    url = myUrl,
                    headers = dict({"User-agent": UserAgent})
                    )
                )
            )
    except urllib2.URLError:
        print myUrl
        lock.acquire()
        itemsToReplace = itemsToReplace - 1
        lock.release()
        return
    fullText = ""
    quotes = page.find("div", "zitat").contents
    for quote in quotes:
        if quote.string.strip() != "":
            fullText = fullText + "\n" + quote.string.strip()
    lock.acquire()
    description.removeChild(description.firstChild)
    cdata = aXml.createCDATASection(fullText)
    description.appendChild(cdata)
    itemsToReplace = itemsToReplace - 1
    lock.release()

feed = "http://feeds2.feedburner.com/gbo-zitate"
page = xml.dom.minidom.parse(urllib2.urlopen(feed))
items = page.getElementsByTagName("item")

# items = items[:30]
itemsToReplace = len(items)
lock = thread.allocate_lock()
for item in items:
    thread.start_new_thread(fullTextItem, (
            item.getElementsByTagName("description")[0],
            item.getElementsByTagName("link")[0].firstChild.nodeValue,
            page
            ))
while itemsToReplace > 0:
    pass

page.getElementsByTagName("atom10:link")[0].setAttribute("href", "http://destroy-club.de/cgi-bin/gbo.rss")

# print page.toprettyxml(encoding="utf-8")
