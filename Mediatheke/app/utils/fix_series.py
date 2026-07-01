"""One-off script: re-run series regex pre-pass on all existing DB entries.

This fixes entries that were tagged with the old (incomplete) patterns.
Run with: pipenv run python -m app.utils.fix_series
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.core.db.database import get_new_db_session
from app.src.services.series_engine import classify_by_rules


def main():
    db = get_new_db_session()

    from app.src.mediaitem.model import MediaItem

    items = (
        db.query(MediaItem)
        .filter(MediaItem.series_name.isnot(None))
        .all()
    )

    print(f"Found {len(items)} items with series metadata, re-classifying…")

    updated = 0
    for item in items:
        result = classify_by_rules(item)
        if result is None:
            continue

        # Normalise: 0 → None (no season/episode)
        new_season = result.season_number if result.season_number else None
        new_episode = result.episode_number if result.episode_number else None

        changed = False

        if result.series_name and result.series_name != item.series_name:
            item.series_name = result.series_name
            changed = True

        if new_season != item.season_number:
            item.season_number = new_season
            changed = True

        if new_episode != item.episode_number:
            item.episode_number = new_episode
            changed = True

        if changed:
            updated += 1
            if updated <= 15:
                print(f"  [{item.id}] {item.title[:60]}… → S{new_season or '?'}E{new_episode or '?'} '{result.series_name}'")

    db.commit()
    print(f"Updated {updated} items.")
    db.close()


if __name__ == "__main__":
    main()
