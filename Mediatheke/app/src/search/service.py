import json
from ..mediaitem.model import MediaItem
from ..mediaitem.schemas import mediaitem_typesense_schema
from ..mediaitem.crud import get_unlimited_media_items
from ...core.db.database import SessionLocal
from typing import List, Optional
import typesense
from sqlalchemy.orm import load_only

class SearchEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating SearchEngine instance")
            cls._instance = super(SearchEngine, cls).__new__(cls)
            cls.client = typesense.Client({
                'nodes': [{
                    'host': 'typesense',
                    'port': '8108',
                    'protocol': 'http'
                }],
                'api_key': 'xyz',
                'connection_timeout_seconds': 2
            })

        return cls._instance

    def media_item_to_json(self, media_item: MediaItem) -> str:
        # Reduced to a single item to avoid holding a large list in memory.
        return json.dumps({
            'id': str(media_item.id),
            'channel': media_item.channel,
            # ... (other fields)
        }) + "\n"

    def create_collection(self):
        self.client.collections.create(mediaitem_typesense_schema)

    def collection_exists(self):
        try:
            self.client.collections['mediaitems'].retrieve()
            return True
        except Exception as e:
            return False

    def delete_collection(self):
        self.client.collections['mediaitems'].delete()

    def get_size(self):
        return self.client.collections['mediaitems'].retrieve()['num_documents']

    def index_media_items(self):
        db = SessionLocal()

        # Batch database queries instead of loading all rows into memory
        batch_size = 500
        offset = 0

        while True:
            print("Querying database starting at offset", offset)

            # Using load_only to reduce the amount of data pulled into RAM
            query = db.query(MediaItem).options(load_only("id", "channel", "topic", "title", "date", "time", "duration"))  # Add all needed fields here
            media_items = query.offset(offset).limit(batch_size).all()

            if not media_items:
                break

            print("Uploading batch to Typesense")
            jsonl_str = "".join([self.media_item_to_json(item) for item in media_items])

            try:
                result = self.client.collections['mediaitems'].documents.import_(jsonl_str)
                if "success" not in result:
                    print(f"Error while importing documents: {result}")
            except Exception as e:
                print(f"Error while importing documents: {e}")

            print(f"Size of media items index: {self.get_size()}")

            offset += batch_size

        db.close()

    # Existing search and get_debugging_info methods

# Your existing get_search_engine function
def get_search_engine():
    return SearchEngine()