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

def strip_variant(title, regex):
    """Strip a variant suffix from a title. Returns stripped title or '' if no match."""
    stripped = re.sub(regex, '', title)
    return stripped if stripped != title else ''

# (regex, field_prefix): ordered by priority, most specific first
VARIANT_DEFS = [
    (r'\s*\(\s*(?:englisch\w*\s+)?Original(?:version|fassung)?\s+mit\s+(?:deutschen\s+)?Untertiteln?\s*\)|\s*\(\s*Om[du]?U\s*\)', 'ov_ut'),
    (r'\s*\(\s*Originalversion\s*\)|\s*\(\s*Originalton\s*\)|\s*\(\s*OV\s*\)|\s+-\s+Originalversion|\s+-\s+Originalton', 'ov'),
    (r'\s*\(\s*mit\s+(?:englischen\s+)?Untertiteln?\s*\)|\s*\(\s*UT\s*\)|\s*\(\s*englische\s+Untertitel\s*\)', 'ut'),
    (r'\s*\(\s*Audiodes(c|k)ription\s*\)|\s+-\s+Audiodes(c|k)ription|Audiodes(c|k)ription', 'audiodescription'),
]

VARIANT_KEYS = ['originalversion', 'omu', 'originalton', '(ov)', 'untertitel', '(ut)', 'audiodes']

def build_urls(mediaitem):
    return {
        'url_video': mediaitem.url_video,
        'url_video_hd': mediaitem.url_video_hd,
        'url_video_low': mediaitem.url_video_low,
    }

def field_name(prefix, quality):
    if prefix == 'audiodescription':
        suffix = 'descriptive_audio'
    else:
        suffix = prefix
    if quality == 'base':
        return f'url_video_{suffix}'
    return f'url_video_{quality}_{suffix}'

def main(dry_run=False):
    db = get_new_db_session()
    series_patterns = load_series_patterns('series-formats.csv')

    mediaitems = db.query(MediaItem).all()

    update_data = []
    title_maps = {variant: {} for _, variant in VARIANT_DEFS}
    variant_ids = {variant: [] for _, variant in VARIANT_DEFS}

    for mediaitem in mediaitems:
        series_data = find_series_data(mediaitem, series_patterns)
        if series_data:
            update_data.append(series_data)

        title_lower = mediaitem.title.lower()
        if not any(kw in title_lower for kw in VARIANT_KEYS):
            continue

        urls = build_urls(mediaitem)
        for regex, variant in VARIANT_DEFS:
            stripped = strip_variant(mediaitem.title, regex)
            if stripped:
                title_maps[variant][stripped] = urls
                variant_ids[variant].append(mediaitem.id)
                break

    # Build URL update data from all variant maps
    url_update_data = []
    for variant, title_map in title_maps.items():
        for mediaitem in mediaitems:
            urls = title_map.get(mediaitem.title)
            if urls:
                update = {'id': mediaitem.id}
                for quality in ['base', 'low', 'hd']:
                    url_key = 'url_video' if quality == 'base' else f'url_video_{quality}'
                    update[field_name(variant, quality)] = urls[url_key]
                url_update_data.append(update)

    total_removed = sum(len(ids) for ids in variant_ids.values())

    if not dry_run:
        if url_update_data:
            print(f'Updating {len(url_update_data)} URLs')
            db.bulk_update_mappings(MediaItem, url_update_data)

        if update_data:
            print(f'Updating {len(update_data)} series attributes')
            db.bulk_update_mappings(MediaItem, update_data)

        if total_removed:
            all_ids = [id for ids in variant_ids.values() for id in ids]
            print(f'Removing {len(all_ids)} variant items')
            db.query(MediaItem).filter(MediaItem.id.in_(all_ids)).delete(synchronize_session=False)

        print('Committing changes')
        db.commit()
    else:
        for data in update_data:
            print(f"Would update {data}")
        for data in url_update_data:
            print(f"Would update {data}")

if __name__ == "__main__":
    main(dry_run=False)
