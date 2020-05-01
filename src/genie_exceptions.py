class GeniusAPIError(Exception):
    def __init__(self, url, status, msg):
        self.message = f"There was an error communicating with the genius API.\n{status}: Unexpected response from '{url}'.\n{msg}"
        self.status = status

class NotFoundError(Exception):
    def __init__(self, search_type, name):
        self.message = f"The {search_type} '{name}' could not be found."

class LyricsParseError(Exception):
    def __init__(self, raw_lyrics):
        self.dump_path = "lyrics_parse_errors.txt"
        self.message = f"There was an unknown error parsing song lyrics. See {self.dump_path} for the raw lyrics that failed to parse."
        self.raw_lyrics = raw_lyrics
        with open(self.dump_path, 'a') as fd:
            fd.write(f"{raw_lyrics}\n---------------------\n")