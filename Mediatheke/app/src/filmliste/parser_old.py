import json
from datetime import datetime, timezone
from dateutil.parser import parse
from ..utils.progressbar import display_progress_bar
import mmap
import ijson
from ..mediaitem.crud import process_batch, create_or_update_media_item
from ..db.database import get_new_db_session
from ..mediaitem.model import MediaItem


class FilmlisteParser:

    @staticmethod
    def clean_json(file_path: str, output_path: str):
        """
        Stream through the JSON and for each 'X', accumulate its values in a separate list.
        """
        master_list = []
        current_list = []

        # This parser will yield each 'X' and its immediate contents one-by-one
        with open(file_path, 'rb') as infile:
            parser = ijson.parse(infile)
            
            for prefix, event, value in parser:
                if prefix == "X":
                    if current_list:  # If there's any previous data in current_list
                        master_list.append(current_list)
                        current_list = []
                elif "X.item" in prefix:
                    current_list.append(value)

            if current_list:  # Don't forget the last batch
                master_list.append(current_list)

        with open(output_path, 'w') as outfile:
            json.dump({"X": master_list}, outfile)

        
    @staticmethod
    def _handle_duplicate_keys(pairs: list) -> dict:
        """Create a dictionary from duplicate keys by appending values to a list."""
        result = {}
        for key, value in pairs:
            if key in result:
                result[key].append(value)
            else:
                result[key] = [value]
        return result

    @staticmethod
    def _parse_json_with_duplicate_keys(data: str) -> dict:
        """Parse JSON data that might contain duplicate keys."""
        return json.loads(data, object_pairs_hook=FilmlisteParser._handle_duplicate_keys)

    @staticmethod
    def _handle_duration(duration_str: str) -> int:
        """Convert a duration string of the form hh:mm:ss to total seconds."""
        if not duration_str:
            return None
        h, m, s = map(int, duration_str.split(":"))
        return h * 3600 + m * 60 + s

    @staticmethod
    def _handle_list_meta(line: str) -> datetime:
        """Convert a datetime string to a datetime object."""
        try:
            return parse(line, dayfirst=True)
        except ValueError:
            return None


    @staticmethod
    def _map_item_to_dict(item: list, current_channel: str, current_topic: str) -> dict:
        """Map list item to a dictionary with descriptive keys."""
        date_object = datetime.strptime(item[3], '%d.%m.%Y').date() if item[3] else None
        time_format = "%H:%M:%S" if len(item[4].split(':')) == 3 else "%H:%M"
        time_object = datetime.strptime(item[4], time_format).time() if item[4] else None

        return {
            'channel': item[0] or current_channel,
            'topic': item[1] or current_topic,
            'title': item[2],
            'date': date_object,
            'time': time_object,
            'duration': FilmlisteParser._handle_duration(item[5]),
            'size_MB': item[6] if item[6] else None,
            'description': item[7],
            'url': item[8],
            'website': item[9],
            'subtitle_url': item[10],
            'rtmp_url': item[11],
            'small_url': item[12],
            'small_rtmp_url': item[13],
            'hd_url': item[14],
            'hd_rtmp_url': item[15],
            'timestamp': FilmlisteParser._handle_list_meta(item[16]),
            'history_url': item[17],
            'geo': item[18],
            'is_new': item[19] == 'true'
        }

    @staticmethod
    def create_media_model(item):
        # A function that converts the processed item dictionary to a SQLAlchemy model instance.
        # Assuming there's a Media model for the purpose of the example.
        return MediaItem(**item)
    
    @classmethod
    def getFilms(cls, file_path: str):
        """Return a list of processed items from the given data file using streaming JSON parsing."""
        filename = "cleaned.json"
        with open(filename, 'r') as f:
            current_channel = ""
            current_topic = ""
            batch_items = []
            index = 0
            objects = json.load(f)['X']
            start_time = datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)
            
            db = get_new_db_session()
            db.autocommit = False
            db.autoflush = False

            for item in objects:
                index += 1
                current_channel = item[0] or current_channel
                current_topic = item[1] or current_topic
                processed_item = cls._map_item_to_dict(item, current_channel, current_topic)
                batch_items.append(processed_item)
                
                if index % 10000 == 0:  # Change to a larger batch size like 10,000 for efficiency
                    try:
                        db.bulk_save_objects([cls.create_media_model(item) for item in batch_items])
                        display_progress_bar(index, len(objects), start_time=start_time.total_seconds())
                        db.commit()
                        batch_items = []
                    except Exception as e:
                        print(f"Error processing batch: {e}")
                        db.rollback()

            # Handle remaining items
            if batch_items:
                try:
                    db.bulk_save_objects([cls.create_media_model(item) for item in batch_items])
                    db.commit()
                except Exception as e:
                    print(f"Error processing batch: {e}")
                    db.rollback()

            db.close()

