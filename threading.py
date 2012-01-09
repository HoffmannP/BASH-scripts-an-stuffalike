#!/usr/bin/python

import thread, urllib2, time

def loadPage(pos):
    global loaded
    specUrl = url % (338514-pos)
    # print specUrl
    try:
        connection = urllib2.urlopen(specUrl)
        p[pos] = connection.read()
    except urllib2.HTTPError as e:
        print e
    loaded = loaded + 1

url = "http://german-bash.org/%i"
n = 50
p = range(n)
loaded = 0



start = time.mktime(time.localtime())
for i in range(n):
    thread.start_new_thread(loadPage, (i,))

while loaded < n:
    pass
end = time.mktime(time.localtime())
print "threaded done in %i seconds" % (end - start)

start = time.mktime(time.localtime())
for i in range(n):
    loadPage(i)
end = time.mktime(time.localtime())
print "serial done in %i seconds" % (end - start)

