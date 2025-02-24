#!env python

import subprocess
import json
import os.path
import sys

import requests
import simple_term_menu

LIMIT=100
BEST_SIZE=1.7*2**10
MAX_EP_PER_SE=1000
SHOWLIST_FILE = 'eztv.json'


def get_show_page(imdb_id, page=0, limit=LIMIT):
    url = f'https://eztvx.to/api/get-torrents?imdb_id={imdb_id}&page={page}&limit={limit}'
    return requests.get(url).json()

def load_show(imdb_id):
    response = get_show_page(imdb_id, limit=1)
    for page in range(1, response['torrents_count'] // LIMIT + 2):
        response = get_show_page(imdb_id, page)
        for torrent in response['torrents']:
            torrent['se'] = MAX_EP_PER_SE * int(torrent['season']) + int(torrent['episode'])
            torrent['size'] = int(torrent['size_bytes']) / 2**20
            yield torrent

def till_field(stream, **kwargs):
    for torrent in stream:
        for key, value in kwargs.items():
            if torrent[key] <= value:
                return
        yield torrent

def filter_field(stream, **kwargs):
    for torrent in stream:
        do_yield = True
        for key, value in kwargs.items():
            if torrent[key] < value:
                do_yield = False
                break
        if do_yield:
            yield torrent

def group_by_se(stream):
    torrents = {}
    for torrent in stream:
        if torrent['se'] in torrents:
            torrents[torrent['se']] += [ torrent ]
        else:
            torrents[torrent['se']] = [ torrent ]
    return torrents

def best_size(torrents):
    optimal = torrents[0]
    for torrent in torrents[1:]:
        if ((torrent['size'] < BEST_SIZE) and (torrent['size'] > optimal['size'])) or \
        ((torrent['size'] > BEST_SIZE) and (torrent['size'] < optimal['size'])):
            optimal = torrent
    return optimal


def episode_list(imdb_id, season, episode=0):
    return { se: best_size(ts) for se, ts in sorted(group_by_se(
        filter_field(
            load_show(imdb_id),
            se=MAX_EP_PER_SE * int(season) + int(episode),
            seeds=1,
            size=300)
        ).items()) }

def match_shows(showlist):
    return { name: episode_list(imdb_id, season, episode) for name, imdb_id, season, episode in showlist }

def print_showlist(se_list):
    for name, episodes in se_list.items():
        print(f'\n{"=" * 5} {name} {"=" * 5}\n')
        for se, torrent in episodes.items():
             season, episode = se // MAX_EP_PER_SE, se % MAX_EP_PER_SE
             print(f'* {season:2d}x{episode:02d}: {torrent["magnet_url"] if torrent is not None else "---"}')
        print('\n')

def all():
    showlist_path = f'{os.path.dirname(__file__)}/{SHOWLIST_FILE}'
    with open(showlist_path, 'r', encoding='utf8') as file:
        showlist = json.load(file)
    print_showlist(match_shows(showlist))

def nice_se(se):
    se, ep = se // MAX_EP_PER_SE, se % MAX_EP_PER_SE
    return f'{se}x{ep}'

def load_list():
    showlist_path = f'{os.path.dirname(__file__)}/{SHOWLIST_FILE}'
    keys = [ 'name', 'imdb_id', 'season', 'episode' ]
    with open(showlist_path, 'r', encoding='utf8') as file:
        return [ { keys[i]: col for i, col in enumerate(show) } for show in json.load(file) ]

def load_dict():
    showlist_path = f'{os.path.dirname(__file__)}/{SHOWLIST_FILE}'
    with open(showlist_path, 'r', encoding='utf8') as file:
        return json.load(file)

def load():
    return load_dict()

def select_show(showlist, select=None):
    show_names = [show['name'] for show in showlist]
    if select in show_names:
        show_index = show_names.index(select)
    else:
        show_selection = simple_term_menu.TerminalMenu([show['name'] for show in showlist])
        show_index = show_selection.show()
    if show_index is None:
        return None, None
    return show_index, showlist[show_index]

def select_episode(show):
    episodes = episode_list(show['imdb_id'], show['season'], show['episode'])
    episode_keys = list(episodes.keys())
    episode_selection = simple_term_menu.TerminalMenu([nice_se(i) for i in episode_keys])
    episode_index = episode_selection.show()
    if episode_index is None:
        return None, None, None
    episode_key = episode_keys[episode_index]
    return episode_key, episodes[episode_key]

def safe(showlist):
    showlist_path = f'{os.path.dirname(__file__)}/{SHOWLIST_FILE}'
    with open(showlist_path, 'w', encoding='utf8') as file:
        json.dump(showlist, file, sort_keys=True, indent=4)

def main():
    # Arguments
    show = None
    args = sys.argv[1:]
    while len(args) > 0:
        if args[0] in [ '--show', '-s' ]:
            show = args[1]
            args = args[2:]
            continue
        print(f'Can not parse {args[0]}')
        args = args[1:]

    showlist = load()

    show_index, show = select_show(showlist)
    if show:
        print(show['name'])
    else:
        print('No show selected')
        safe(showlist)
        return

    episode_key, episode = select_episode(show)
    if episode:
        print(nice_se(episode_key))
    else:
        print('No episode selected')
        safe(showlist)
        return

    # Saving changes
    showlist[show_index]['season'] = episode['season']
    showlist[show_index]['episode'] = episode['episode']
    safe(showlist)

    # Start torrent/magnet link
    subprocess.call(['xdg-open', episode['magnet_url']])


if __name__ == '__main__':
    main()