"""
we have a csv like this. this csv defines patterns how we can filter items in our db and find series elements

example, regex, series_identifier, with_season, channel
(Staffel 1, Folge 56), \(Staffel (\d+), Folge (\d+)\), topic, true, ard
(S01/E05), \(S(\d+)\/E(\d+)\), topic,true, ard
Staffel 2, F
Folge 1, Folge (\d+), title, false, hr
Episode 1, Episode (\d+), title, false, all
"""

from typing import List, Tuple, Optional
import re
import csv
import json
from datetime import datetime
from time import time
from ....core.db.database import get_new_db_session
from ...mediaitem.model import MediaItem

db = get_new_db_session()
series_file = open('series-formats.csv', 'r')
series_reader = csv.reader(series_file, delimiter=';')
series = []
# Skip header
next(series_reader)
for row in series_reader:
    series.append(row)
series_file.close()

# Fetch all media items
mediaitems = db.query(MediaItem).all()

update_data = []
update_titles = []
items_to_remove = []
dry_run = False
# Iterate through each media item to update its data
for mediaitem in mediaitems:
    for series_pattern in series:
        if series_pattern:
            regex = series_pattern[1]
            match = re.search(regex, mediaitem.title)
            if match:
                with_season = series_pattern[3] == 'true'
                
                season_digit = int(series_pattern[5])
                episode_digit = int(series_pattern[6])
                
                if season_digit == 0:
                    season_number = None
                    episode_number = match.group(episode_digit)
                else:
                    season_number = match.group(season_digit)
                    episode_number = match.group(episode_digit)
                
                # Debug: Print the season and episode numbers
                
                series_identifier = series_pattern[2]
                series_name = mediaitem.topic if series_identifier == 'topic' else re.sub(regex, '', mediaitem.title)

                channel = series_pattern[4]
                
                # Store the data to be updated
                update_data.append({
                    'id': mediaitem.id,
                    'season_number': season_number,
                    'episode_number': episode_number,
                    'series_name': series_name,
                })
                
                break
    if "audiodes" in mediaitem.title.lower():
        # this has nothing to do with series, but we want to remove this mediaitem but add its urls to another mediaitem with the same title (but without "(Audiodes(c/k)ription) or " - Audiodes(c/k)ription" in the title)
        # remove the Audiodes(c/k)ription from the title could be written with c or k
        title = re.sub(r'(Audiodes(c|k)ription)|(\s-\sAudiodes(c|k)ription)', '', mediaitem.title)
        # add the title to the list of titles to update
        if title == None:
            print(f'Error: title is None for mediaitem {mediaitem.title}')
        
        update_title = {
            'title': title,
            'urls_to_update': {
                'url_video_descriptive_audio': mediaitem.url_video,
                'url_video_hd_descriptive_audio': mediaitem.url_video_hd,
                'url_video_low_descriptive_audio': mediaitem.url_video_low,
            }
        }
        update_titles.append(update_title)
        items_to_remove.append(mediaitem.id)
        
# Create a mapping of titles to URLs to update
title_to_urls_map = {item['title']: item['urls_to_update'] for item in update_data if 'urls_to_update' in item}

# Initialize empty list for URL update data
url_update_data = []

# Create a mapping of cleaned titles to URLs to update
title_to_urls_map = {item['title']: item['urls_to_update'] for item in update_titles}

# Initialize empty list for URL update data
url_update_data = []

# Iterate over media items to collect the URL update data
for mediaitem in mediaitems:
    urls_to_update = title_to_urls_map.get(mediaitem.title)
    if urls_to_update:
        url_update_data.append({
            'id': mediaitem.id,
            **urls_to_update
        })

# Do the bulk update for URLs if there is any data to update and if it's not a dry run.
if url_update_data and not dry_run:
    print(f'Updating {len(url_update_data)} URLs')
    db.bulk_update_mappings(MediaItem, url_update_data)

# If you have data for series and other attributes, do that bulk update as well.
if update_data and not dry_run:
    print(f'Updating {len(update_data)} series attributes')
    db.bulk_update_mappings(MediaItem, update_data)

if items_to_remove and not dry_run:
    print(f'Removing {len(items_to_remove)} mediaitems')
    db.query(MediaItem).filter(MediaItem.id.in_(items_to_remove)).delete(synchronize_session=False)

# Commit all changes.
if not dry_run:
    print('Committing changes')
    db.commit()

# Handle the dry-run scenario
elif dry_run:
    for data in update_titles:
        print(f"would update {data}")
        #print(f"would update {data['id']} with season {data['season_number']} and episode {data['episode_number']} and series name {data['series_name']} and channel {data['channel']}")