import json
from ..mediaitem.model import MediaItem
from ..mediaitem.schemas import mediaitem_typesense_schema
from ..mediaitem.crud import get_unlimited_media_items
from ...core.db.database import SessionLocal
from typing import List, Optional
import typesense

class SearchEngine:
  _instance = None

  def __new__(cls):
    if cls._instance is None:
        print("Creating SearchEngine instance")
        cls._instance = super(SearchEngine, cls).__new__(cls)
        
        # Your Typesense client setup here
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

  def media_items_to_jsonl(self, media_items: List[MediaItem]) -> str:
    jsonl_str = ""
    for media_item in media_items:
        json_obj = json.dumps({
            'id': str(media_item.id),
            'channel': media_item.channel,
            'topic': media_item.topic,
            'title': media_item.title,
            'date': media_item.date.strftime("%Y-%m-%d") if media_item.date else "",
            'time': media_item.time.strftime("%H:%M:%S") if media_item.time else "",
            'duration': media_item.duration,
            'size_MB': media_item.size_MB,
            'description': media_item.description or "",
            'url_video': media_item.url_video,
            'url_website': media_item.url_website,
            'url_subtitle': media_item.url_subtitle,
            'url_video_low': media_item.url_video_low,
            'url_video_hd': media_item.url_video_hd,
            'url_video_descriptive_audio': media_item.url_video_descriptive_audio or "",
            'url_video_low_descriptive_audio': media_item.url_video_low_descriptive_audio or "",
            'url_video_hd_descriptive_audio': media_item.url_video_hd_descriptive_audio or "",
            'thumbnail': media_item.thumbnail or "",
            'episode_number': int(media_item.episode_number) if media_item.episode_number else 0,
            'season_number': int(media_item.season_number) if media_item.season_number else 0,
            'series_name': media_item.series_name or "",
        })
        jsonl_str += json_obj + "\n"
    return jsonl_str
  
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
    # Get all media items from the database
    db = SessionLocal()
    media_items = get_unlimited_media_items(db)
    db.close()

    # Index the media items
    batch_size = 5000  # Experiment with this number
    for i in range(0, len(media_items), batch_size):
      print("Indexing batch starting with index", i)

      batch = media_items[i:i+batch_size]
      jsonl_str = self.media_items_to_jsonl(batch)
      del batch
      print("Uploading batch to Typesense")
      try:
          result = self.client.collections['mediaitems'].documents.import_(jsonl_str)
          if "success" not in result:
              print(f"Error while importing documents: {result}")
      except Exception as e:
        print(f"Error while importing documents: {e}")      
      print(f"Size of media items index: {self.get_size()}")

  def search(self, query: str, query_by: Optional[str] = 'channel,topic,title,description,series_name'):
    result = self.client.collections['mediaitems'].documents.search({
      'q': query,
      'query_by': query_by
    })
    return result

  def get_debugging_info(self):
    """
    return all collections, and interesting info about them
    """

    collections = self.client.collections.retrieve()
    collection_info = {"collections": []}

    for collection in collections:
        collection_name = collection["name"]

        # Fetch the schema for this collection
        schema = self.client.collections[collection_name].retrieve()

        # Maybe get some sample documents too, let's say 3
        documents = self.client.collections[collection_name].documents.search(
            {"q": "*", "query_by": "title", "per_page": 3}
        )["hits"]

        # You can also fetch other stats if needed
        stats = self.client.collections[collection_name].retrieve()  # Or some custom stats endpoint if Typesense supports it later on

        collection_info["collections"].append({
            "name": collection_name,
            "num_documents": collection["num_documents"],
            "schema": schema,
            "sample_documents": documents,
            "stats": stats
        })

    return collection_info


# Create a method to get a single instance of SearchEngine
def get_search_engine():
    return SearchEngine()

