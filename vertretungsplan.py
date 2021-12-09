#!/usr/bin/env python3

import json
import requests
import datetime
import tempfile
import os
import locale
import subprocess
import camelot

CONFIG_FILE = '~/.config/newspoint_config.json'
LAST_CHANGE_FILE = '~/.config/newspoint_lastchange.json'

def main():
    last_change_file_name = os.path.expanduser(LAST_CHANGE_FILE)
    locale.setlocale(locale.LC_ALL, ('de_DE', 'UTF-8'))
    try:
        with open(last_change_file_name) as f:
            last_change = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        last_change = {}
    response = requests.get('https://newspointweb.de/mobile/appdata.ashx', params={ 'request': 'list', 'client': str(CLIENT_ID)})
    plaene = response.json()
    inhalte = {}

    for vertretungsplan in plaene['objects']:
        date = datetime.datetime(*[int(d) for d in vertretungsplan['caption'].split(' ')[-1].split('.')[::-1]])
        date_ts = str(int(date.timestamp()))
        change = datetime.datetime.fromtimestamp(int(vertretungsplan['changed'][6:-10]))
        if datetime.datetime.combine(date, datetime.datetime.max.time()) < datetime.datetime.now():
            if date_ts in last_change:
                del last_change[date_ts]
            continue
        if date_ts in last_change and datetime.datetime.fromtimestamp(last_change[date_ts]) >= change:
            continue
        inhalte[date] = {
            'change': change,
            'eintraege': [row for row in readVertretungsplan(vertretungsplan['downloadUrl']) if CLASS_NAME in row[2]]}
        last_change[date_ts] = change.timestamp()
    with open(last_change_file_name, 'w') as f:
        json.dump(last_change, f)
    result = printVertretungsplan(inhalte)
    if result is not None:
        sendSignalTo(SIGNAL_ACCOUNT, SINGAL_TARGET, result)

def readVertretungsplan(url):
    response = requests.get(url)
    filename = tempfile.mkstemp(suffix='.pdf')[1]
    with open(filename, 'wb') as tmp:
        tmp.write(response.content)
    tables = camelot.read_pdf(filename,pages='all')
    os.unlink(filename)
    return [[cell.replace('\n', ' ') for cell in row] for table in tables for row in table.data[1:]]

def printVertretungsplan(inhalte):
    lines = []
    for date in inhalte:
        inhalt = inhalte[date]
        if len(inhalt['eintraege']) == 0:
            continue
        lines.append(f'Vertretungsplan für {date.strftime("%A, den %x")} (letzte Aktualiserung von {inhalt["change"].strftime("%c")})')
        for line in inhalt['eintraege']:
            lines.append('\t'.join(line))
        lines.append('')
    if len(lines) == 0:
        return None
    return '\n'.join(lines).strip()

def sendSignalTo(account, target, send_text):
    subprocess.run([
        'signal-cli',
        '-u', account,
        'send',
        *target],
        input=send_text,
        text=True,
        check=True,
        stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    try:
        with open(os.path.expanduser(CONFIG_FILE)) as f:
            config = json.load(f)
            CLIENT_ID = config['client']['id']
            CLIENT_PW = config['client']['password']
            CLASS_NAME = config['classname']
            SIGNAL_ACCOUNT = config['signal']['account']
            SINGAL_TARGET = config['signal']['target']
    except (FileNotFoundError, json.decoder.JSONDecodeError, IndexError) as error:
        print(error)
        os.exit(1)
    main()
