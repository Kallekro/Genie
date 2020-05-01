import json

class Song:
    def __init__(self):
        self.title  = None
        self.artist = None
        self.url    = None
        self.lyrics = None
        self.raw = None
        self.cached = False

    def initialize_from_download(self, song_data):
        self.title = song_data["title"]
        self.artist = song_data["primary_artist"]["name"]
        self.url = song_data["url"]
        self.raw = song_data

    def initialize_from_cache(self, cached_song):
        if isinstance(cached_song, str):
            with open(cached_song, 'r') as song_fd:
                song_json = json.load(song_fd)
        else:
            song_json = cached_song
        self.title  = song_json["meta"]["title"]
        self.artist = song_json["meta"]["artist"]
        self.url    = song_json["meta"]["url"]
        self.lyrics = song_json["lyrics"]
        self.raw    = song_json["raw"]
        self.cached = True

    def dump(self):
        return {
            "meta": {
                "title"  : self.title,
                "artist" : self.artist,
                "url"    : self.url
            },
            "lyrics" : self.lyrics,
            "raw"    : self.raw
        }