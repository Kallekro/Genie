import sys
import os
import json
import argparse
import traceback
import shutil

from api_handler import *
from objects import Song
import misc

def update_lyrics(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("artist")
    parser.add_argument("-f", "--force", action="store_true")
    args = parser.parse_args(args)
    safe_api_call(lambda: get_songs_by_artist(args.artist, args.force))

def get_songs_by_artist(artist, force_update):
    print(f"Finding songs by '{artist}'")
    artist_id = find_artist_id(artist)

    if force_update:
        print("Forcing cached songs update...")
        with open(misc.CACHE_PATH, 'r+') as fd:
            cache_json = json.load(fd)
            try:
                del cache_json["artists"][artist]
            except:
                print("Artist was not found in cache. Ignoring --force-update.")

    song_objs = import_cached_songs(artist)
    print(f"Found {len(song_objs)} cached songs.")

    download_songs(artist_id, artist, song_objs)
    save_songs(song_objs)

def import_cached_songs(artist):
    song_objs = {}
    print("Importing previously downloaded songs...")
    with open(misc.CACHE_PATH, 'r') as fd:
        cache_json = json.load(fd)
        try:
            songs = cache_json["artist"]
        except KeyError:
            return {}
    for song_json in songs.values():
        song_objs[new_song_obj.title] = init_cached_song(song_json)
    return song_objs

def save_songs(song_objs):
    print("Caching freshly downloaded song(s)...")
    for song in song_objs.values():
        if song.cached: continue
        save_single_song(song)

def save_single_song(song_obj):
    with open(misc.CACHE_PATH, 'r+') as fd:
        cache_json = json.load(fd)
        if song_obj.artist not in cache_json["artists"]:
            cache_json["artists"][song_obj.artist] = {"songs": {}}
        cache_json["artists"][song_obj.artist]["songs"][song_obj.title] = song_obj.dump()
        fd.truncate(0)
        fd.seek(0)
        json.dump(cache_json, fd)

def find_lyrics(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("song")
    args = parser.parse_args(args)

    safe_api_call(lambda: get_specific_song(args.song))

def get_specific_song(song_query):
    song_query_split = song_query.split('/')
    if len(song_query_split) > 1:
        artist = song_query_split[0]
        song_name = song_query_split[1]
    else:
        artist = None
        song_name = song_query_split[0]

    print("Searching for lyrics in cache...")
    song_json = check_cached_songs(artist, song_name)
    if song_json == None:
        print("Lyrics not found in cache.")
        print("Downloading lyrics...")
        song_obj = download_single_song(song_name, artist)
        print("Caching downloaded song.")
        save_single_song(song_obj)
    else:
        song_obj = init_cached_song(song_json)
    print("Finished. Displaying lyrics:\n---------------------------------------")
    print(song_obj.lyrics)

def check_cached_songs(artist, song_name):
    with open(misc.CACHE_PATH, 'r') as fd:
        cache_json = json.load(fd)
        if artist != None:
            try:
                return cache_json["artists"][artist]["songs"][song_name]
            except KeyError:
                return None
        else:
            for art in cache_json["artists"].values():
                try:
                    return art["songs"][song_name]
                except KeyError:
                    continue
            return None

def init_cached_song(song_json):
    new_song_obj = Song()
    new_song_obj.initialize_from_cache(song_json)
    return new_song_obj

def clean_cache():
    os.remove(misc.CACHE_PATH)

def main():
    if not os.path.isfile(misc.CACHE_PATH):
        with open(misc.CACHE_PATH, 'w') as fd:
            json.dump({"artists" : {}}, fd)

    main_parser = argparse.ArgumentParser(description='Fun with Genius API')
    main_parser.add_argument('--update', action="store_true", help="Downloads all songs by given artist.")
    main_parser.add_argument('--clean-cache', action="store_true")
    main_parser.add_argument('args', nargs=argparse.REMAINDER)
    main_args = main_parser.parse_args()

    if main_args.update:
        update_lyrics(main_args.args)
    elif main_args.clean_cache:
        clean_cache()
    else:
        find_lyrics(main_args.args)

if __name__ == "__main__":
    main()