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
        self.title  = cached_song["meta"]["title"]
        self.artist = cached_song["meta"]["artist"]
        self.url    = cached_song["meta"]["url"]
        self.lyrics = cached_song["lyrics"]
        self.raw    = cached_song["raw"]
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