from typing import List
import re
import csv
from ....core.db.database import get_new_db_session
from ...mediaitem.model import MediaItem

# Function to load series patterns from CSV
def load_series_patterns(file_path: str) -> List[List[str]]:
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader)  # Skip header
        return [row for row in reader]

# Function to find series data using patterns
def find_series_data(mediaitem, patterns):
    for pattern in patterns:
        if pattern:
            regex, series_identifier, with_season, channel = pattern[1], pattern[2], pattern[3] == 'true', pattern[4]
            match = re.search(regex, mediaitem.title)
            if match:
                season_number = match.group(1) if with_season else None
                episode_number = match.group(2) if with_season else match.group(1)
                series_name = mediaitem.topic if series_identifier == 'topic' else re.sub(regex, '', mediaitem.title)
                return {
                    'id': mediaitem.id,
                    'season_number': season_number,
                    'episode_number': episode_number,
                    'series_name': series_name,
                }
    return None

# Function to update media item URLs for audiodescription
def update_audiodescription(mediaitem, title_to_urls_map):
    title = re.sub(r'(Audiodes(c|k)ription)|(\s-\sAudiodes(c|k)ription)', '', mediaitem.title)
    if title:
        title_to_urls_map[title] = {
            'url_video_descriptive_audio': mediaitem.url_video,
            'url_video_hd_descriptive_audio': mediaitem.url_video_hd,
            'url_video_low_descriptive_audio': mediaitem.url_video_low,
            'ignore': True  # Set flag to ignore
        }

def main(dry_run=False):
    db = get_new_db_session()
    series_patterns = load_series_patterns('series-formats.csv')

    mediaitems = db.query(MediaItem).all()

    update_data = []
    title_to_urls_map = {}
    
    for mediaitem in mediaitems:
        # Check for series pattern matches and prepare update data
        series_data = find_series_data(mediaitem, series_patterns)
        if series_data:
            update_data.append(series_data)
        
        # Handle audiodescription media items
        if "audiodes" in mediaitem.title.lower():
            update_audiodescription(mediaitem, title_to_urls_map)
    
    # Prepare URL update data
    url_update_data = [
        {'id': mediaitem.id, **urls_to_update}
        for mediaitem in mediaitems
        if (urls_to_update := title_to_urls_map.get(mediaitem.title))
    ]

    # Perform bulk updates if not a dry run
    if not dry_run:
        if url_update_data:
            print(f'Updating {len(url_update_data)} URLs')
            db.bulk_update_mappings(MediaItem, url_update_data)
        
        if update_data:
            print(f'Updating {len(update_data)} series attributes')
            db.bulk_update_mappings(MediaItem, update_data)
        
        print('Committing changes')
        db.commit()
    
    # Handle the dry-run scenario
    else:
        for data in update_data:
            print(f"Would update {data}")
        for data in url_update_data:
            print(f"Would update {data}")

if __name__ == "__main__":
    main(dry_run=False)
