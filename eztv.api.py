#!env python

import requests

LIMIT=100
BEST_SIZE=1.7*2**10
MAX_EP_PER_SE=1000

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

def main():
    showlist = [
        ["Chicago Fire", 2261391, 12, 0],
        ["Chicago PD", 2805096, 11, 0],
        ["Chicago Med", 4655480, 9, 0],
        ["The Handmaid's Tale", 5834204, 6, 0],
        ["S.W.A.T.", 6111130, 7, 0],
        ["9-1-1", 7235466, 7, 0],
        ["9-1-1 Lone Star", 10323338, 5, 0],
        ["Special Ops: Lioness", 13111078, 2, 0],
        ["The Bear", 14452776, 2, 0]]
    print_showlist(match_shows(showlist))

if __name__ == '__main__':
    main()