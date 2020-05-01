from lxml import etree
from io import StringIO
import json
import re
from genie_exceptions import *

import time

WHITESPACE_PATTERN = re.compile(r"\s*(.*)\s+([\s\S]*)\/")
LYRICS_UNRELEASED_PATTERN = re.compile(r"Lyrics for this song have yet to be released. Please check back once the song has been released.")

PARSER = etree.HTMLParser()

def parse(resp):
    tree = etree.parse(StringIO(resp), PARSER)

    for element in tree.getroot().iter():
        if element.tag == "div":
            if "class" in element.attrib and element.attrib["class"] == "lyrics":
                return get_raw_text(element)

def get_raw_text(root):
    res = ""
    for element in root.iter():
        if element.text:
            res += element.text
        if element.tail:
            res += element.tail
    return clean_lyrics(res)

def clean_lyrics(lyrics):
    lyrics = lyrics.replace("\\n", "\n").replace("sse", "").replace('\\', '')
    clean = re.search(WHITESPACE_PATTERN, lyrics)
    try:
        return f"{clean.group(1)}\n{clean.group(2)}"
    except AttributeError:
        lyrics_unreleased = re.search(LYRICS_UNRELEASED_PATTERN, lyrics)
        if lyrics_unreleased != None:
            return "[UNRELEASED]"
        raise LyricsParseError(lyrics)