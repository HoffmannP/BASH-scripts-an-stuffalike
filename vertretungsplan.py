#!/usr/bin/env python3

import json
import requests
import sys
import typing
import datetime
import tempfile
import os
import locale
import subprocess
import math
import tabula

CONFIG_FILE = '~/.config/newspoint_config.json'
LAST_CHANGE_FILE = '~/.config/newspoint_lastchange.json'
NAMES_FILE = '~/.config/newspoint_namefile.json'

CONFIG: typing.Dict[str, typing.Union[str, bool]] = {
    'ignore_last_change': False,
    'last_change_file': '~/.config/newspoint_lastchange.json',
    'names_file': '~/.config/newspoint_namefile.json',
    'print_output': False
}
NAMES: typing.Dict[str, str] = {}

def isNaN(variable):
    return isinstance(variable, float) and math.isnan(variable)

def parseCommandline(config):
    flags = sys.argv[1:]
    while len(flags) > 0:
        # print(flags)
        if flags[0] in ['--force', '-f']:
            config['ignore_last_change'] = True
            flags = flags[1:]
            continue
        if flags[0] in ['--class', '-c']:
            config['classname'] = flags[1].split(',')
            flags = flags[2:]
            continue
        if flags[0] in ['--print', '-p']:
            config['print_output'] = True
            flags = flags[1:]
            continue
    return config



def main():
    global NAMES
    locale.setlocale(locale.LC_ALL, ('de_DE', 'UTF-8'))

    last_change_file_name = os.path.expanduser(CONFIG['last_change_file'])
    if len(sys.argv) > 1 and sys.argv[1] in ['--force', '-f']:
        last_change = {}
    else:
        try:
            with open(last_change_file_name) as f:
                last_change = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            last_change = {}

    names_file_name = os.path.expanduser(CONFIG['names_file'])
    try:
        with open(names_file_name) as f:
            NAMES = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pass

    response = requests.get('https://newspointweb.de/mobile/appdata.ashx', params={ 'request': 'list', 'client': str(CONFIG['client']['id'])})
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
        try:
            inhalte[date] = {
                'change': change,
                'eintraege': [row for row in readVertretungsplan(vertretungsplan['downloadUrl']) if any(cn in str(row[1]) for cn in CONFIG['classname'])]}
        except TypeError as e:
            print(readVertretungsplan(vertretungsplan['downloadUrl']))
            raise e
        last_change[date_ts] = change.timestamp()

    result = printVertretungsplan(inhalte)
    if CONFIG['print_output']:
        if result is not None:
            print(result)
        else:
            print('[empty]')
    else:
        if result is not None:
            sendSignalTo(CONFIG['signal']['account'], CONFIG['signal']['target'], result)

    with open(last_change_file_name, 'w') as f:
        json.dump(last_change, f)


def readVertretungsplan(url):
    response = requests.get(url)
    filename = tempfile.mkstemp(suffix='.pdf')[1]
    with open(filename, 'wb') as tmp:
        tmp.write(response.content)
    tables = tabula.read_pdf(filename, pages='all')
    os.unlink(filename)

    table = []
    table_list = [t.values.tolist() for t in tables]
    rows = [(row[:-2] + [row[-1]] if len(row) == 8 else row) for row in [
        (row[:-1] if isNaN(row[-1]) else row) for table in table_list for row in table]]
    # print(rows)

    if len(rows) == 0:
        return table

    previous_row = rows[1][1:]
    for row in rows[2:]:
        if isNaN(row[1]):
            for i, last in enumerate(previous_row):
                if len(row) < i + 2:
                    print(f'Zeile ist zu kurz {i}+1 vs. {len(row)}: "{row}"')
                    break
                if not isNaN(row[i+1]):
                    previous_row[i] = f'{last} {row[i+1]}'
        else:
            table.append(previous_row)
            previous_row = row[1:]
    table.append(previous_row)
    return table

def fullname(shortname):
    global NAMES
    if isNaN(shortname):
        return '-'
    if '/' in shortname:
        name1, name2 = shortname.split('/', 1)
        return f'{fullname(name1)}, {fullname(name2)}'
    if shortname in NAMES:
        return NAMES[shortname]
    NAMES[shortname] = shortname
    search = f'$$("div.name").map(d => d.textContent.trim()).filter(t => Array.from("{shortname}").every(l => t.includes(l)))'
    print(f'Konnte den Namen »{shortname}« nicht finden [{search}]')
    return shortname

def printVertretungsplan(inhalte):
    lines = []
    for date in inhalte:
        inhalt = inhalte[date]
        if len(inhalt['eintraege']) == 0:
            continue
        lines.append(f'Vertretungsplan für {date.strftime("%A, den %x")} (Aktualisierung von {inhalt["change"].strftime("%c")})')
        for eintrag in inhalt['eintraege']:
            stunde, klasse, fach, ausfLehr, ersatzLehr, notiz = eintrag
            fachString = '' if isNaN(fach) else f' {fach}'
            ausfLehr = fullname(ausfLehr)
            ersatzLehr = fullname(ersatzLehr)
            ersatzLehrerString = '' if isNaN(ersatzLehr) else f' → {ersatzLehr}'
            ausfLehrerString = ersatzLehrerString if isNaN(ausfLehr) else f' ({ausfLehr}{ersatzLehrerString})'
            lines.append(f'Klasse {klasse}: {stunde} Stunde{fachString}{ausfLehrerString}: {notiz}')
        lines.append('')
    if len(lines) == 0:
        return None
    return '\n'.join(lines).strip()

def sendSignalTo(account, target, send_text):
    subprocess.run([
        '/usr/local/bin/signal-cli',
        '-u', account,
        'send',
        *target,
        '--message-from-stdin'],
        input=send_text,
        text=True,
        check=True,
        stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    with open(os.path.expanduser(CONFIG_FILE)) as f:
        CONFIG = z = {**json.load(f), **CONFIG}
    CONFIG = parseCommandline(CONFIG)
    main()
