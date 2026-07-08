from ...celery import app
from ..filmliste.parser import parse_filmliste
from ..filmliste.crud import create_import_event, get_last_import_event
from ..filmliste.model import FilmlisteImportEvent
from ..mediaitem.model import MediaItem
from ..mediaitem.crud import process_batch
from ...core.db.database import get_new_db_session

from datetime import datetime, timezone
import time
import logging
import requests
from celery import chain


@app.task()
def import_filmliste(full: bool = True):
    db = get_new_db_session()

    if full:
        logging.info("Full import: marking all existing items as potentially stale")
        db.query(MediaItem).update({MediaItem.ignore: True}, synchronize_session=False)
        db.commit()

    logging.info("Importing filmliste")
    items, timestamp = parse_filmliste(full=full)
    BATCH_SIZE = 10000
    db = get_new_db_session()
    len_items = len(items)
    timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(tzinfo=None)
    import_event: FilmlisteImportEvent  = create_import_event(db=db, timestamp=timestamp, full_import=full, media_item_count=len_items)
    if import_event is None:
      print("Import event already exists", flush=True)
      return
    print(f"Created import event {import_event}", flush=True)
    db.add(import_event)
    added_items = 0
    time_start = time.time()
    for i in range(0, len_items, BATCH_SIZE):
      batch = items[i:i + BATCH_SIZE]
      added_items = added_items + process_batch(db, batch, import_event, full_import=full)
      time_spent = time.time() - time_start
      time_spent_human_readable = time.strftime("%H:%M:%S", time.gmtime(time_spent))
      calculated_time_left = (len_items - i) * (time_spent / (i + 1))
      logging.info(f"Processed batch {i} of {len_items}, Will be done in {time.strftime('%H:%M:%S', time.gmtime(calculated_time_left))}, Time spent: {time_spent_human_readable}")

    import_event.media_item_count = added_items
    db.commit()

    chain(
        run_make_series.s(),
        reload_recommendations.s(),
    ).delay()

    if full:
        from ..search.tasks import reindex_typesense
        reindex_typesense.delay()


@app.task()
def run_make_series(dry_run=False):
    """Bulk series classification and variant cleanup after import."""
    from ..mediaitem.scripts.make_series import main as _main
    _main(dry_run=dry_run)


@app.task(autoretry_for=(Exception,), max_retries=3, default_retry_delay=30)
def reload_recommendations():
    """Reload the server's recommendation engine and clear its cache."""
    requests.post(
        "http://server:8000/series-detection/reload-recommendations",
        timeout=120,
    )
    logging.info("Reloaded recommendation engine on server")


@app.task()
def daily_full_import():
    """Full import that runs once per day to catch deletions."""
    import_filmliste(full=True)

@app.task()
def check_for_updates():
    db = get_new_db_session()
    last_import_event = get_last_import_event(db)

    if not last_import_event or (datetime.utcnow() - last_import_event.timestamp).total_seconds() > 14400:
        # Import full Filmliste if no import has happened in the last 4 hours
        import_filmliste(full=True)
    else:
        # Import diff Filmliste if an import has happened in the last 4 hours
        import_filmliste(full=False)


