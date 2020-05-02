# Genie
Fun with the Genius.com API.

## Current features
* Download, cache and display lyrics for a specific song.
  Only downloads if the song is not cached.
* Download and cache all songs by a specific artist.
  Only downloads the songs that are not already cached.

## How to use
Use the `run.sh` script to run genie.
* A single argument means searching for lyrics to a specific song, and the argument is the search query. The search query can be the song name or a combination of artist and song name, e.g. "Radiohead/Airbag".
* Use the `--update` option and specify an artist to update cache with songs by that artist.
  * Use `-f` or `--force` to force re-download of previously cached songs.
* Use `--clean-cache` to delete the entire cache.

You can set up the following alias to use genie from anywhere:
`alias genie='/mnt/c/Users/kalle/Documents/devel/Genie/run.sh'`