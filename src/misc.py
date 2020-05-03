import os

CACHE_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/../.cache.json"
# TODO: Optimize cache read/write by sharing global file pointer
CACHE_FP   = None

VERBOSE = False

def make_valid_path(s):
    return "".join([x if x.isalnum() else "_" for x in s])
