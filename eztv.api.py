#!env python

import subprocess
import requests
import simple_term_menu
import json
import os.path

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

def filter_minimum(stream, **kwargs):
    for torrent in stream:
        for key, value in kwargs.items():
            if torrent[key] < value:
                continue
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
        filter_minimum(
            till_field(
                load_show(imdb_id),
                se=MAX_EP_PER_SE * season + episode),
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
    print_showlist(match_shows(showlist))

def nice_se(se):
    se, ep = se // MAX_EP_PER_SE, se % MAX_EP_PER_SE
    return f'{se}x{ep}'

def main():
    showlist_path = f'{os.path.dirname(__file__)}/{SHOWLIST_FILE}'
    with open(showlist_path, 'r', encoding='utf8') as file:
        showlist = json.load(file)
    show_selection = simple_term_menu.TerminalMenu([name for name, _, _, _ in showlist])
    show_index = show_selection.show()
    show = showlist[show_index]
    print(show[0])
    episodes = episode_list(*show[1:])
    episode_selection = simple_term_menu.TerminalMenu([nice_se(i) for i in episodes.keys()])
    episode_index = episode_selection.show()
    episode_key = list(episodes.keys())[episode_index - 1]
    if episode_index > 0:
        episode_prev = list(episodes.keys())[episode_index - 1]
        showlist[show_index][2] = episode_prev // MAX_EP_PER_SE
        showlist[show_index][3] = episode_prev % MAX_EP_PER_SE
        with open(showlist_path, 'w', encoding='utf8') as file:
            json.dump(showlist, file, sort_keys=True, indent=4)
    episode_prev = list(episodes.keys())[episode_index - 1]
    episode = episodes[episode_key]
    # subprocess.run(["kitty", "icat", episode['small_screenshot']])
    subprocess.call(['xdg-open', episode['magnet_url']])


if __name__ == '__main__':
    main()