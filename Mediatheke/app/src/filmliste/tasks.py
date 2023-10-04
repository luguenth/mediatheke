from ...celery import app
from ..filmliste.parser import parse_filmliste
from ..filmliste.crud import create_import_event
from ..filmliste.model import FilmlisteImportEvent
from ..mediaitem.crud import process_batch
from ...core.db.database import get_new_db_session

from datetime import datetime
import time
import logging

@app.task()
def import_filmliste():
  logging.info("Importing filmliste")
  items, timestamp = parse_filmliste(full=True)
  BATCH_SIZE = 2500
  db = get_new_db_session()
  len_items = len(items)
  #convert timestamp to datetime
  timestamp = datetime.fromtimestamp(timestamp)
  import_event: FilmlisteImportEvent  = create_import_event(db=db, timestamp=timestamp, media_item_count=len_items)
  if import_event is None:
    print("Import event already exists", flush=True)
    return
  print(f"Created import event {import_event}", flush=True)
  db.add(import_event)
  added_items = 0
  time_start = time.time()
  for i in range(0, len_items, BATCH_SIZE):
    batch = items[i:i + BATCH_SIZE]
    added_items = added_items + process_batch(db, batch, import_event)
    time_spent = time.time() - time_start
    time_spent_human_readable = time.strftime("%H:%M:%S", time.gmtime(time_spent))
    calculated_time_left = (len_items - i) * (time_spent / (i + 1))
    logging.info(f"Processed batch {i} of {len_items}, Will be done in {time.strftime('%H:%M:%S', time.gmtime(calculated_time_left))}, Time spent: {time_spent_human_readable}")
  
  import_event.media_item_count = added_items
  db.commit()


