"""
This code was mainly translated from:
https://github.com/mediathekview/mediathekviewweb/blob/master/server/FilmlisteParser.ts

The original code was written in TypeScript and is licensed under the GNU General Public License v3.0

The original code was written by:
Patrick Hein (@bagbag)
Kaspar V. (@casaper)
"""

import requests
import lzma
from datetime import datetime, timezone
import json
from io import TextIOWrapper
import re
from time import time
from typing import List, Tuple
from ...core.config import get_settings

def create_url_from_base(base_url: str, new_url: str) -> str:
    """
    Creates a new URL from a base URL and the hd or low URL.
    """
    new_split = new_url.split('|')
    if len(new_split) == 2:
        return base_url[:int(new_split[0])] + new_split[1]
    return ""

def handle_list_meta(line: str) -> int:
    """
    Handles the first line of the Filmliste file.
    """
    match = re.search(r'".*?","(\d+)\.(\d+)\.(\d+),\s?(\d+):(\d+)"', line)
    if match:
        return int(datetime(
            year=int(match.group(3)),
            month=int(match.group(2)),
            day=int(match.group(1)),
            hour=int(match.group(4)),
            minute=int(match.group(5)),
            tzinfo=timezone.utc
        ).timestamp())
    return 0

def handle_duration(duration_str: str) -> int:
    """
    Convert a duration string of the form hh:mm:ss to total seconds.
    """
    if not duration_str:
        return 0
    h, m, s = map(int, duration_str.split(":"))
    return h * 3600 + m * 60 + s

def map_list_line_to_item(line: str, current_channel: str, current_topic: str) -> Tuple[str, str, dict]:
    """
    Maps a line from the Filmliste to a dict.
    """
    try:
        parsed = json.loads(line)
    except json.decoder.JSONDecodeError:
        return "", "", {}


    current_channel = parsed[0] if parsed[0] else current_channel
    current_topic = parsed[1] if parsed[1] else current_topic
    
    if parsed[5]:  # Check if hr_duration is not empty
        duration = handle_duration(parsed[5])
    else:
        duration = 0

    if parsed[6]:
        size = int(parsed[6]) * 1024 * 1024  # MB to bytes
    else:
        size = 0

    date_object = datetime.strptime(parsed[3], '%d.%m.%Y').date() if parsed[3] else None
    time_format = "%H:%M:%S" if len(parsed[4].split(':')) == 3 else "%H:%M"
    time_object = datetime.strptime(parsed[4], time_format).time() if parsed[4] else None

    
    return current_channel, current_topic, {
        'channel': current_channel,
        'topic': current_topic,
        'title': parsed[2],
        'description': parsed[7],
        'timestamp': parsed[16],
        'date': date_object,
        'time': time_object,
        'duration': duration,
        'size_MB': size,
        'url_website': parsed[9],
        'url_subtitle': parsed[10],
        'url_video': parsed[8],
        'url_video_low': create_url_from_base(parsed[8], parsed[12]),
        'url_video_hd': create_url_from_base(parsed[8], parsed[14])
    }

def get_random_mirror() -> str:
    """
    Returns a random mirror from the list of mirrors.
    """

    mirrors = get_settings().filmliste_mirrors.split(',')

    return mirrors[int(time()) % len(mirrors)]

def stream_decompressed_lines(url: str):
    """
    Generator function to yield decompressed lines from an xz compressed HTTP stream.
    This minimizes RAM usage by processing each line as it is read.
    """
    with requests.get(url, stream=True) as response:
        decompressor = lzma.LZMADecompressor()
        buffer = ""
        left_over_bytes = b""  # Store leftover bytes that can't be decoded

        for chunk in response.iter_content(chunk_size=1024):
            # Decompress and attempt to decode UTF-8, appending any leftover bytes from previous chunks
            decompressed_chunk = decompressor.decompress(chunk)
            try:
                decoded_chunk = (left_over_bytes + decompressed_chunk).decode('utf-8')
                left_over_bytes = b""
            except UnicodeDecodeError:
                # Keep the last byte and try to decode it with the next chunk
                left_over_bytes = decompressed_chunk[-1:]
                decompressed_chunk = decompressed_chunk[:-1]
                decoded_chunk = (left_over_bytes + decompressed_chunk).decode('utf-8', 'ignore')
                left_over_bytes = b""

            buffer += decoded_chunk

            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                yield line


def parse_filmliste(full: bool = True) -> Tuple[List[dict], int]:
    url = f'https://{get_random_mirror()}/Filmliste-{"akt" if full else "diff"}.xz'
    print(f'Parsing Filmliste from {url}')
    
    line_number = 0
    current_channel, current_topic = "", ""
    items = []
    timestamp = 0

    for line in stream_decompressed_lines(url):
        line_number += 1
        if line_number == 1:
            continue
        if line_number == 2:
            timestamp = handle_list_meta(line)
            continue

        current_channel, current_topic, entry = map_list_line_to_item(line, current_channel, current_topic)
        if not entry.get('title'):
            continue

        items.append(entry)
        
    print('Finished processing Filmliste')
    return items, timestamp
