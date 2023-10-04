from ...celery import app
from ..search import service
import logging


@app.task()
def init_typesense(force_delete=False):
    logging.info("Initializing Typesense")
    search_engine = service.get_search_engine()
    
    if not search_engine.collection_exists():
        logging.info("Media items collection does not exist. Creating it.")
        search_engine.create_collection()
    
    if force_delete:
        logging.info("Deleting the media items collection.")
        search_engine.delete_collection()
        logging.info("Creating the media items collection.")
        search_engine.create_collection()
        
    size = search_engine.get_size()
    logging.info("Media items collection size: %s", size)
    
    if size < 300000:
        logging.info("Indexing media items.")
        search_engine.index_media_items()
        
    logging.info("Initializing Typesense done.")