#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time

# the fields in discstats are:
# majId
# minId
# dev
# rMerged
# secRead
# milsecRead
# wrCompl
# wMerged
# secWrite
# milsecWrite
# IOprocess
# IOsec
# IOWsec

# Initialization
DISCKSTATS = '/proc/diskstats'
old = {}
new = {}
with open(DISCKSTATS, 'r', encoding='utf8') as f:
    for line in f:
        parts = line.split()
        dev = parts[2]
        new[dev] = [float(i) for i in parts[3:]]

# Running
while True:
    time.sleep(2)
    with open(DISCKSTATS, 'r', encoding='utf8') as f:
        for line in f:
            parts = line.split()
            dev = parts[2]
            old[dev], new[dev] = new[dev], [float(i) for i in parts[3:]]
        if new[dev][5] != old[dev][5]:
            READ =  '{(512 * (new[dev][4]-old[dev][4]) / (new[dev][5]-old[dev][5])):5.0f}'
        else:
            if new[dev][4] == old[dev][4]:
                READ = '    0'
            else:
                READ = '    ∞'
        if new[dev][9] != old[dev][9]:
            WRITE =  '{(512 * (new[dev][8]-old[dev][8]) / (new[dev][9]-old[dev][9])):5.0f}'
        else:
            if new[dev][8] == old[dev][8]:
                WRITE = '    0'
            else:
                WRITE = '    ∞'
        print(f'{dev:6s}: r/w: {READ}/{WRITE} [b/s]')
