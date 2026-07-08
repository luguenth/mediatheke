from ...celery import app
from ..search import service
import logging


@app.task(autoretry_for=(Exception,), max_retries=3, default_retry_delay=10)
def init_typesense(force_delete=False):
    logging.info("Initializing Typesense")
    search_engine = service.get_search_engine()
    
    if not search_engine.collection_exists():
        logging.info("Media items collection does not exist. Creating it.")
        search_engine.create_collection()
    
    if force_delete:
        logging.info("Deleting the media items collection.")
        try:
            search_engine.delete_collection()
        except Exception:
            logging.info("Collection already gone, continuing.")
        logging.info("Creating the media items collection.")
        search_engine.create_collection()
        
    size = search_engine.get_size()
    logging.info("Media items collection size: %s", size)
    
    if size < 300000:
        logging.info("Indexing media items.")
        search_engine.index_media_items()
        
    logging.info("Initializing Typesense done.")


@app.task(autoretry_for=(Exception,), max_retries=2, default_retry_delay=60)
def reindex_typesense():
    """Force-rebuild the Typesense index from the current database state."""
    logging.info("Force-reindexing Typesense")
    init_typesense(force_delete=True)
    logging.info("Typesense reindex complete")