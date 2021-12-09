#!/usr/bin/env python3

import json
import requests
import datetime
import tempfile
import os
import locale
import subprocess
import camelot

CLIENT_ID = 103193
CLIENT_PW = ''
# CLASS_NAME = '6c'
CLASS_NAME = '7c'
LAST_CHANGE_FILE = '~/.config/newspoint_lastchange.json'
SINGAL_TARGET = ['-g', 'B1xWwtduKuDwwYGrGr0XSZwljyraWFJH6MegAhoaBD8=']


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
        sendSignalTo(SINGAL_TARGET, result)

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

def sendSignalTo(number, send_text):
    subprocess.run([
        '/home/ber/Downloads/signal-cli-0.9.2/bin/signal-cli',
        '-u', '+491715761382',
        'send',
        *number],
        input=send_text,
        text=True,
        stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    main()
