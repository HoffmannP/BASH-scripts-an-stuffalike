#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

""" Initialization """
ds = '/proc/diskstats'
old = {}
new = {}
f = open(ds, 'r')
for line in f:
    # [majId, minId, dev, rMerged, secRead, milsecRead, wrCompl, wMerged, secWrite, milsecWrite, IOprocess, IOsec, IOWsec]
    parts = line.split()
    dev = parts[2]
    new[dev] = [float(i) for i in parts[3:]]
f.close()

""" running """
while True:
    time.sleep(2)
    f = open(ds, 'r')
    for line in f:
        # [majId, minId, dev, rMerged, secRead, milsecRead, wrCompl, wMerged, secWrite, milsecWrite, IOprocess, IOsec, IOWsec]
        parts = line.split()
        dev = parts[2]
        old[dev], new[dev] = new[dev], [float(i) for i in parts[3:]]
	if new[dev][5] != old[dev][5]:
	    read =  '%5.0f' % (512 * (new[dev][4]-old[dev][4]) / (new[dev][5]-old[dev][5]))
        else:
	    if new[dev][4] == old[dev][4]:
		read = '    0'
	    else:
       	        read = '    ∞'
	if new[dev][9] != old[dev][9]:
	    write =  '%5.0f' % (512 * (new[dev][8]-old[dev][8]) / (new[dev][9]-old[dev][9]))
        else:
	    if new[dev][8] == old[dev][8]:
		write = '    0'
	    else:
       	        write = '    ∞'
	print '%6s: r/w: %s/%s [b/s]' % (dev, read, write)
    f.close()
