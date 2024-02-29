#!/usr/bin/env python

import glob
import pathlib
import os
import os.path
import shutil
import sys

MCA_PATERN = 'r.*.*.mca'
WORLD_FOLDERS = [ 'entities', 'poi', 'region' ]

JSON_PATTERN = '*.dat'
PLAYERS_FOLDERS = [ 'playerdata' ]

def readArguments():
    keep = sys.argv[1]
    if not pathlib.Path(keep).is_absolute():
        keep = pathlib.Path.home() / '.minecraft' / 'saves' / keep
    add = sys.argv[2]
    if not pathlib.Path(add).is_absolute():
        add = pathlib.Path.home() / '.minecraft' / 'saves' / add
    if len(sys.argv) > 3:
        offsetPair = sys.argv[3].split(',')
        offset = { 'x': int(offsetPair[0]), 'y': int(offsetPair[1]) }
    else:
        offset = None
    return keep, add, offset

def coordinates(name):
    parts = name.split('.')
    return {
        'name': name,
        'x': int(parts[1]),
        'y': int(parts[2])}

def searchWorlds(path):
    root = pathlib.Path(path)
    # world = { name: glob.glob(f'{name}/{MCA_PATERN}', root_dir=root) for name in WORLD_FOLDERS }
    os.chdir(root)
    world = { name: glob.glob(f'{name}/{MCA_PATERN}') for name in WORLD_FOLDERS }
    coordinatedWorld = { name: [ coordinates(file) for file in world[name] ] for name in world }
    return { 'path': path, 'world': coordinatedWorld, **areaShape(coordinatedWorld) }

def areaShape(world):
    area = world[WORLD_FOLDERS[0]]
    Xs = [ entry['x'] for entry in area ]
    Ys = [ entry['y'] for entry in area ]
    geometry = {
        'entries': len(area),
        'min': { 'x': min(Xs), 'y': min(Ys) },
        'max': { 'x': max(Xs), 'y': max(Ys) },
        'size': { 'x': max(Xs) - min(Xs) + 1, 'y': max(Ys) - min(Ys) + 1 } }
    shape = [ [' '] * geometry['size']['x'] for i in range(geometry['size']['y']) ]
    for entry in area:
        shape[entry['y'] - geometry['min']['y']][entry['x'] - geometry['min']['x']] = 'X' if entry['x'] == 0 and entry['y'] == 0 else '#'
    return { 'geometry': geometry, 'shape': shape }

def shapeString(world):
    return '\n'.join([''.join(line) for line in world['shape']])

def copyWorldFiles(keep, add, offset):
    print(f'Using offset x={offset["x"]} y={offset["y"]}')
    for folder in add['world']:
        for file in add['world'][folder]:
            shutil.copy2(
                f'{add["path"]}/{file["name"]}',
                f'{keep["path"]}/{folder}/{movedFilename(file, offset)}')

def movedFilename(file, offset):
    return f'r.{file["x"] + offset["x"]}.{file["y"] + offset["y"]}.mca'

def mergeWorlds(keep, add, offset=None):
    worldKeep = searchWorlds(keep)
    print(worldKeep['geometry']); print(shapeString(worldKeep))
    worldAdd = searchWorlds(add)
    print(worldAdd['geometry']); print(shapeString(worldAdd))
    if offset is None:
        offset = {
            'x': worldKeep['geometry']['max']['x'] + 1 - worldAdd['geometry']['min']['x'],
            'y': worldKeep['geometry']['min']['y'] - worldAdd['geometry']['min']['y'] }
    copyWorldFiles(worldKeep, worldAdd, offset)
    worldMerged = searchWorlds(keep)
    print(worldMerged['geometry']); print(shapeString(worldMerged))

def searchPlayers(path):
    root = pathlib.Path(path)
    # players = glob.glob(f'{PLAYERS_FOLDERS[0]}/{JSON_PATTERN}', root_dir=root)
    os.chdir(root)
    players = glob.glob(f'{PLAYERS_FOLDERS[0]}/{JSON_PATTERN}')
    return { 'path': path, 'ids': [ playerFile.split('/')[1].split('.')[0] for playerFile in players ] }

def searchPlayerFiles(path, name):
    root = pathlib.Path(path)
    # players = glob.glob(f'{PLAYERS_FOLDERS[0]}/{JSON_PATTERN}', root_dir=root)
    os.chdir(root)
    return glob.glob(f'**/{name}.*')

def copyPlayerFiles(keep, add):
    for player in add['ids']:
        if player in keep['ids']:
            continue
        print(player)
        for file in searchPlayerFiles(add['path'], player):
            shutil.copy2(
                f'{add["path"]}/{file}',
                f'{keep["path"]}/{file}')

def mergePlayers(keep, add):
    playersKeep = searchPlayers(keep)
    playersAdd = searchPlayers(add)
    copyPlayerFiles(playersKeep, playersAdd)

def main():
    keep, add, offset = readArguments()
    print(keep, add, offset)
    mergeWorlds(keep, add, offset)
    mergePlayers(keep, add)


if __name__ == '__main__':
    main()
