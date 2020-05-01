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

    output_dir, artist_cached = misc.get_cache_dir(artist)

    if force_update and artist_cached:
        print("Forcing cached songs update...")
        shutil.rmtree(output_dir)
        artist_cached = False

    if not artist_cached:
        os.makedirs(output_dir)
        song_objs = {}
    else:
        song_objs = import_cached_songs(artist, output_dir) if artist_cached else {}
        print(f"Found {len(song_objs)} cached songs.")

    download_songs(artist_id, artist, song_objs)
    save_songs(song_objs, output_dir)

def import_cached_songs(artist, output_dir):
    song_objs = {}
    print("Importing previously downloaded songs...")
    for song_path in os.listdir(output_dir):
        song_path = os.path.join(output_dir, song_path)
        if not os.path.isfile(song_path): continue
        new_song_obj = Song()
        new_song_obj.initialize_from_cache(song_path)
        song_objs[new_song_obj.title.lower()] = new_song_obj
    return song_objs

def save_songs(song_objs, output_dir):
    print("Caching freshly downloaded song(s)...")
    for song in song_objs.values():
        if song.cached: continue
        save_single_song(song, output_dir)

def save_single_song(song_obj, output_dir):
    with open(f"{output_dir}/{misc.make_valid_path(song_obj.title)}_lyrics.json", 'w') as fd:
        json.dump(song_obj.dump(), fd)

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
    song_obj = check_cached_songs(artist, song_name)
    if song_obj == None:
        print("Lyrics not found in cache.")
        print("Downloading lyrics...")
        song_obj = download_single_song(song_name, artist)

        output_dir, artist_cached = misc.get_cache_dir(song_obj.artist)
        if not artist_cached:
            os.makedirs(output_dir)
        print("Caching downloaded song.")
        save_single_song(song_obj, output_dir)
    print("Finished. Displaying lyrics:\n---------------------------------------")
    print(song_obj.lyrics)

def check_cached_songs(artist, song_name):
    for root, dirnames, filenames in os.walk(misc.CACHE_DIR):
        root_split = os.path.split(root)
        if os.path.basename(root_split[0]) != "lyrics": continue
        if artist != None and misc.make_valid_path(artist) != root_split[1]: continue
        for filename in filenames:
            with open(os.path.join(root, filename), 'r') as fd:
                song_json = json.load(fd)
                if song_json["meta"]["title"] == song_name:
                    new_song_obj = Song()
                    new_song_obj.initialize_from_cache(song_json)
                    return new_song_obj
    return None

def clean_cache():
    shutil.rmtree(misc.CACHE_DIR)
    os.makedirs(misc.CACHE_DIR)

def main():
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