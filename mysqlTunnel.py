#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import tempfile
import sys
import csv
import os.path
import os

port = 3306

"""
server.csv is a file containing in the first column your servers name (for
your eyes) and the servers address (for your computer)
"""
ServerFile = 'server.csv'


def getPid(call):
    processes = tempfile.TemporaryFile()
    subprocess.call(['ps', 'aux'], stdout=processes)
    for process in processes:
        parts = process.split(11)
        if call in parts[11]:
            return parts[1]
    return False


def processRunning(pid):
    processes = tempfile.TemporaryFile()
    subprocess.call(['ps', 'aux'], stdout=processes)
    for process in processes:
        if pid == process.split()[1]:
            return True
    return False


def processName(pid):
    f = open('/proc/%s/comm' % str(pid), 'r')
    return f.read()


def usingPort(port):
    processes = tempfile.TemporaryFile()
    subprocess.call(['netstat', '-ptan'], stdout=processes, stderr=processes)
    for process in processes:
        parts = process.split()
        if parts[3].split(':')[1] == port:
            if parts[6] != '-':
                pid, name = parts[6].split('/')
            else:
                pid, name = None, None
            return {
                'state': parts[5],
                'pid': pid,
                'name': name
            }
    return False


def zenity_yesno(text):
    return subprocess.call(['zenity', '--question', '--text=%s' % text]) == 0


def zenity_info(text):
    return subprocess.call(['zenity', '--info', '--text=%s' % text])


def zenity_list(text, header, optionen):
    call = ['zenity', '--list', '--text=%s' % text, '--radiolist']
    for column in header:
        call.append('--column=%s' % column)
    for zeile in optionen:
        for feld in zeile:
            call.append(feld)
    retVal = tempfile.TemporaryFile()
    if subprocess.call(call, stdout=retVal):
        return False
    retVal.seek(0)
    return retVal.read()


def killprocess(pid):
    subprocess.call(['kill', pid])
    processes = tempfile.TemporaryFile()
    subprocess.call(['ps', 'auxf'], stdout=processes)
    return not processRunning(pid=pid)


def openTunnel(address):
    return subprocess.call([
        '/usr/bin/ssh',
        '-c', 'blowfish',
        '-NL', '%d:localhost:%d' % (port, port),
        address
    ])

# check if programm is already running
pid = getPid('%d:localhost:%d' % (port, port))
if pid is not False:
    if zenity_yesno('Eine andere Instanz dieses Programms läuft bereits. \
Soll diese beendet werden? (ansonsten wird diese Aktion abgebrochen'):
        if not killprocess(pid):
            zenity_info('still running')
            sys.exit(1)
    else:
        print zenity_info('exiting')
        sys.exit(0)

# check if port is already used
using = usingPort(port)

if using is not False:
    if 'WAIT' in using['state']:
        zenity_info('Der Port %i wird zur Zeit noch von %s genutzt, bitte \
später erneut versuchen' % (port, using['pid']))
        sys.exit(1)

    if using['pid'] is not None:
        if zenity_yesno('Der Port %i ist bereits durch das Programm %s \
belegt. Soll dieses beendet werden? (ansonsten wird diese Aktion abgebrochen)'
                        % (port, using['name'])):
            if not killprocess(pid):
                zenity_info('still running')
                sys.exit(2)
        else:
            zenity_info('exiting')
            sys.exit(0)
    else:
        zenity_info('must be root (probably mysqld)')

selection = []
servers = {}
ServerFile = os.path.dirname(__file__) + os.sep + ServerFile
for line in csv.reader(file(ServerFile, 'rb')):
    selection.append(['0', line[0]])
    servers[line[0].strip()] = line[1].strip()


server = zenity_list(
    'MySQL Server auswählen',
    ['✓', 'Server'],
    selection).strip()
if server is False or server == '':
    zenity_info('Kein Server ausgewählt')
    sys.exit(3)

while True:
    code = openTunnel(servers[server])
    zenity_info('Verbindung gestorben mit Code %d, verbinde neu…' % code)
