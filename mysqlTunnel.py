#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import tempfile
import sys
import csv
import os.path
import os
import time
import gettext


def getPids(call):
    mypid = os.getpid()
    pids = []
    for process in subprocess.check_output(['ps', 'x', '--noheaders']).split("\n"):
        if process == '':
            continue
        parts = process.split(None, 4)
        if not call in parts[4]:
            continue
        pid = int(parts[0])
        if pid == mypid:
            continue
        pids.append(pid)
    if len(pids) > 0:
        return pids
    return False


def processRunning(pid):
    for process in subprocess.check_output(['ps', 'x', '--noheaders']).split("\n"):
        if process == '':
            continue
        if pid == int(process.split()[0]):
            return True
    return False


def processName(pid):
    f = open('/proc/%s/comm' % str(pid), 'r')
    return f.read()


def usingPort(port):
    for process in subprocess.check_output(['netstat', '-ptan'], stderr=file('/dev/null', 'w')).split("\n"):
        if process == '':
            continue
        parts = process.split()
        if len(parts) > 2 and ':' in parts[3] and parts[3].split(':')[1] == str(port):
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
    try:
        children = subprocess.check_output(['ps', '-o', 'pid', '--ppid', str(pid), '--noheaders']).split("\n")
    except subprocess.CalledProcessError:
        children = []
    os.kill(pid, 15)
    for child in children:
        if child == '':
            continue
        killprocess(int(child))
    return not processRunning(pid)


def openTunnel(address, port):
    return subprocess.call([
        '/usr/bin/ssh',
        '-c', 'blowfish',
        '-NL', '%d:localhost:%d' % (port, port),
        address
    ])


def readConfig(config):
    selection = []
    servers = {}
    with file(os.path.dirname(__file__) + os.sep + config, 'rb') as f:
        for line in csv.reader(f):
            selection.append(['0', line[0]])
            servers[line[0].strip()] = line[1].strip()
    return (servers, selection)
""" server.csv is a file containing in the first column your servers name
(for your eyes) and the servers address (for your computer) """


def checkRunning(programm):
    pids = getPids(programm)
    if not pids:
        return
    for pid in pids:
        if not zenity_yesno(_('%s already running, kill?') % programm):
            zenity_info(_('exiting'))
            sys.exit(0)

        killed = killprocess(pid)
        if not killed:
            zenity_info(_('failed to kill running %s, exiting') % programm)
            sys.exit(1)


def checkPortFree(port):
    used = usingPort(port)
    if not used:
        return

    if used['name'] is None:
        zenity_info(_('port used, can\'t kill'))
        sys.exit(2)

    while (used['state'] == 'WAIT') and zenity_yesno(_('port used by "%s", wait for 5 secs?') % used['name']):
        time.sleep(5)
        used = usingPort(port)
        if not used:
            return

    if not zenity_yesno(_('port used by "%s", kill?') % used['name']):
        zenity_info(_('exiting'))
        sys.exit(0)

    killed = killprocess(int(used['pid']))
    if not killed:
        zenity_info(_('failed to kill, exiting'))
        sys.exit(3)


def selectServer(selection):
    server = zenity_list(
        _('select MySQL server'),
        ['✓', _('server')],
        selection)
    if server is False or server.strip() == '':
        zenity_info(_('no server selected'))
        sys.exit(4)
    return server.strip()


def main(port, serverFile):
    servers, selection = readConfig(serverFile)
    checkRunning(os.path.basename(__file__))
    checkPortFree(port)
    server = selectServer(selection)

    openTunnel(servers[server], port)
    while zenity_yesno(_('connection broke, reconnect?')):
        openTunnel(servers[server], port)

t = gettext.translation('mysqlTunnel', '/home/ber/bin')
_ = t.lgettext
if __name__ == '__main__':
    main(port=3306, serverFile='server.csv')
