import os

CACHE_DIR = f"{os.path.dirname(os.path.abspath(__file__))}/../.cache"
VERBOSE = False

def make_valid_path(s):
    return "".join([x if x.isalnum() else "_" for x in s])

def get_cache_dir(artist):
    output_dir = f"{CACHE_DIR}/lyrics/{make_valid_path(artist)}"
    artist_cached = os.path.isdir(output_dir)
    return output_dir, artist_cached