import sys
import requests
import json
from multiprocessing import Pool

from genie_exceptions import *
from objects import Song
import lyrics_parser
import misc
MAX_PAGES = 2

def safe_api_call(fn):
    try:
        fn()
    except GeniusAPIError as err:
        print(err.message)
        traceback.print_exc()
    except NotFoundError as err:
        print(err.message)
    except LyricsParseError as err:
        print(err.message)

def dump_response(resp, name):
    with open(f"{name}_dump.json", 'w') as outfd:
        json.dump(resp, outfd)

def get_api_response(request_url, parameters={}):
    full_url = f'https://api.genius.com/{request_url}'
    response = requests.get(
        full_url,
        headers={'Authorization': 'Bearer z1DQufqnVL807Pv4GeBB9e5mqyGYu0mCjVRXhU2MUHn5XXJ-KudZ291KNq-HKnkz'},
        params=parameters
    ).json()

    if response["meta"]["status"] != 200:
        raise GeniusAPIError(full_url, response["meta"]["status"], response["meta"]["message"])

    return response["response"]

def get_search_response(query):
    return get_api_response(f"search?q={query}")

def find_artist_id(artist):
    search_resp = get_search_response(artist)

    artist_id = next((hit["result"]["primary_artist"]["id"] for hit in search_resp["hits"] if hit["result"]["primary_artist"]["name"] == artist), None)
    if artist_id:
        return artist_id
    else:
        raise NotFoundError("artist", artist)

def download_songs(artist_id, artist, song_objs):
    import_len = len(song_objs)
    sys.stdout.write("Browsing genius pages: ")
    for page_i in range(1, MAX_PAGES + 1):
        sys.stdout.write(f"{page_i} ")
        sys.stdout.flush()
        song_resp = get_api_response(f"artists/{artist_id}/songs", {"per_page": 50, "page": page_i})
        get_song_objects(song_resp["songs"], song_objs, artist)
        if song_resp["next_page"] == None:
            break
        page_i += 1
    sys.stdout.write('\n')
    print(f"Found {len(song_objs)} songs.")
    if import_len == len(song_objs):
        print("All songs were found in cache.")
    else:
        print("Downloading song lyrics...")
        download_lyrics_async([so for so in list(song_objs.values()) if not so.cached])
        print("Lyrics downloaded.")

def download_single_song(song_name, artist):
    song_query = f"{song_name} {artist if artist else ''}"
    resp = get_search_response(song_query)
    if len(resp["hits"]) == 0 or (artist and resp["hits"][0]["result"]["primary_artist"]["name"].lower() != artist.lower()):
        raise NotFoundError("song", song_name if not artist else f"{artist}/{song_name}")
    song_data = resp["hits"][0]["result"]
    new_song_obj = Song()
    new_song_obj.initialize_from_download(song_data)

    print("Song found. Downloading lyrics...")
    new_song_obj.lyrics = download_lyrics(new_song_obj)
    return new_song_obj

def download_lyrics_async(song_objs):
    with Pool() as p:
        all_lyrics = p.map(download_lyrics, song_objs)
    for i, song in enumerate(song_objs):
        song_objs[i].lyrics = all_lyrics[i]

def download_lyrics(song):
    full_html = str(requests.get(song.url).content)
    return lyrics_parser.parse(full_html)

def get_song_objects(songs, song_objs, artist):
    for song_data in songs:
        if song_data["title"] in song_objs or song_data["primary_artist"]["name"] != artist:
            continue
        new_song_obj = Song()
        new_song_obj.initialize_from_download(song_data)
        song_objs[new_song_obj.title.lower()] = new_song_obj
