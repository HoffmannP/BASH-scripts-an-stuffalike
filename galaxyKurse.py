#!/usr/bin/env python3

import re
import json
import subprocess
import requests
from bs4 import BeautifulSoup

COURSES_DB = '.courses.json'

def get_entry(a):
    return {
        "title": re.sub(r'[ \n]+', ' ', re.sub(r'€\xa0[,\d]+|10x60 Min.', '', '\n'.join([a.get_text() for a in a.select('.table-row')]))).strip(),
        "link": 'https://shop.jenaer-baeder.de' + a['href'],
        "id": a['href'].split('=')[-1]}


def load_courses():
    response = requests.get('https://shop.jenaer-baeder.de/courses/category/')
    soup = BeautifulSoup(response.text, 'lxml')

    return filter(
        lambda a: 'Seepferdchen' in a['title'] and 'Hermsdorf' not in a['title'],
        [get_entry(a) for a in soup.select('#articles > a')])

def load_old():
    try:
        with open(COURSES_DB, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.decoder.JSONDecodeError:
        return {}

old_courses = load_old()
for c in load_courses():
    if c['id'] not in old_courses:
        subprocess.run([
            '/home/ber/Downloads/signal-cli-0.9.2/bin/signal-cli',
            '-u', '+491715761382',
            'send',
            '+491715761382'],
            input=f'{c["title"]}\n{c["link"]}', text=True,
            stdout=subprocess.DEVNULL)
        old_courses[c['id']] = ( c['title'], c['link'] )

with open(COURSES_DB, 'w') as f:
    json.dump(old_courses, f)