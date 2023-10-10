from typing import Union, List, TypeVar
from sqlalchemy.orm import Session, Query
from sqlalchemy import func, or_, text, tuple_, and_, asc, desc
from sqlalchemy.exc import IntegrityError
from collections import defaultdict
from unidecode import unidecode

from .model import MediaItem
from ..filmliste.model import FilmlisteImportEvent

from ..topic.model import Topic
from ..channel.model import Channel
from ..user.model import User, Recommendation


from ..thumbnail import service

from ..mediaitem import schemas


T = TypeVar('T', Topic, Channel, MediaItem)

def _get_or_create(db: Session, model: T, filter_by: dict, **kwargs) -> T:
    """
    Returns existing record or creates a new one if it does not exist.
    """
    instance = db.query(model).filter_by(**filter_by).first()
    if not instance:
        instance = model(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
    return instance

def get_or_create_topic(db: Session, topic_name: str) -> Topic:
    return _get_or_create(db, Topic, {'name': topic_name}, name=topic_name)

def get_or_create_channel(db: Session, channel_name: int) -> Channel:
    return _get_or_create(db, Channel, {'name': channel_name}, name=channel_name)

def get_or_create_media_item(db: Session, media_item: dict) -> MediaItem:
    topic = get_or_create_topic(db, media_item['topic'])
    channel = get_or_create_channel(db, media_item['channel'])
    media_item_data_to_insert = media_item.copy()
    media_item_data_to_insert['topic_id'] = topic.id
    media_item_data_to_insert['channel_id'] = channel.id
    return _get_or_create(db, MediaItem, {
        'title': media_item['title'],
        'topic_id': topic.id,
        'channel_id': channel.id,
        'date': media_item['date'],
        'time': media_item['time']
    }, **media_item_data_to_insert)

def _filter_query_by_params(query, **kwargs) -> 'Query':
    """
    Helper function to filter the query based on provided kwargs.
    """
    #always oder by date and time
    query = query.order_by(MediaItem.date.desc(), MediaItem.time.desc())
    if kwargs.get('random_order'):
        query = query.order_by(func.random())
    if kwargs.get('with_thumbnail'):
        query = query.filter(MediaItem.thumbnail != None)
    if kwargs.get('longer_than'):
        query = query.filter(MediaItem.duration > kwargs['longer_than'])
    if kwargs.get('newer_than'):
        query = query.filter(MediaItem.date > kwargs['newer_than'])
    return query

def _handle_existing_item_check(db: Session, item: dict) -> Union[None, MediaItem]:
    """
    Checks if an item exists and returns it. If not, returns None.
    """
    return db.query(MediaItem).filter_by(
        title=item['title'],
        topic_id=item['topic_id'],
        channel_id=item['channel_id'],
        date=item['date'],
        time=item['time']
    ).first()

def process_batch(db: Session, batch: list[dict], import_event: FilmlisteImportEvent) -> int:
    try:
        added = get_or_create_media_item_bulk(db, batch, import_event)
        db.commit()
        return added
    except Exception as e:
        print(f"Error processing batch: {e}")
        db.rollback()
        return 0

def get_existing_media_items_by_urls_and_timestamps(db: Session, url_timestamp_pairs: list[tuple[str, str]]) -> dict:
    query = db.query(MediaItem).filter(tuple_(MediaItem.url_website, MediaItem.timestamp).in_(url_timestamp_pairs))
    return {(item.url_website, item.timestamp): item for item in query}

def get_media_item_by_channel_topic_title(db: Session, channel: str, topic: str, title: str) -> MediaItem:
    return db.query(MediaItem).filter(MediaItem.channel == channel, MediaItem.topic == topic, MediaItem.title == title).first()

def get_or_create_media_item_bulk(db: Session, media_items: list[dict], import_event: FilmlisteImportEvent) -> int:
    unique_url_timestamps = set()
    url_timestamp_pairs = [(item['url_website'], item['timestamp']) for item in media_items]
    existing_media_items = get_existing_media_items_by_urls_and_timestamps(db, url_timestamp_pairs)

    new_media_items = []
    for item in media_items:
        url_website = item['url_website']
        timestamp = item['timestamp']
        
        if (url_website, timestamp) in unique_url_timestamps:
            continue

        if (url_website, timestamp) in existing_media_items:
            continue

        try:
            topic = get_or_create_topic(db, item['topic'])
            channel = get_or_create_channel(db, item['channel'])

            if topic and channel:
                item.update({'topic_id': topic.id, 'channel_id': channel.id})
                if not _handle_existing_item_check(db, item):
                    item_data_to_insert = item.copy()
                    item_data_to_insert.update({
                        'topic_id': topic.id,
                        'channel_id': channel.id,
                        'import_event_id': import_event.id
                    })
                    new_media_items.append(MediaItem(**item_data_to_insert))
                    unique_url_timestamps.add((url_website, timestamp))
            else:
                print(f"Error with topic or channel for item: {item}")

        except Exception as e:
            print(f"Error with item: {item}")
            print(e)

    if new_media_items:
        try:
            db.bulk_save_objects(new_media_items)
            db.commit()
            return len(new_media_items)
        except IntegrityError as ie:
            print(f"Integrity error when adding new media items: {ie}")
            db.rollback()
            return 0
    return 0


def get_media_item(db: Session, media_item_id: int) -> MediaItem:
    return db.query(MediaItem).filter(MediaItem.id == media_item_id).first()

def create_or_update_media_item(db: Session, media_item: dict) -> MediaItem:
    media_item = get_or_create_media_item(db, media_item)
    return media_item


def get_all_media_items(db: Session, skip: int = 0, limit: int = 100, **kwargs) -> List[MediaItem]:
    query = db.query(MediaItem)
    query = _filter_query_by_params(query, **kwargs)
    return query.offset(skip).limit(limit).all()

def get_unlimited_media_items(db: Session, **kwargs) -> List[MediaItem]:
    query = db.query(MediaItem)
    query = _filter_query_by_params(query, **kwargs)
    return query.all()

def update_media_item(db: Session, media_item_id: int, updated_data: dict) -> MediaItem:
    media_item = get_media_item(db, media_item_id)
    for key, value in updated_data.items():
        setattr(media_item, key, value)
    db.commit()
    db.refresh(media_item)
    return media_item

def delete_media_item(db: Session, media_item_id: int) -> None:
    db.delete(get_media_item(db, media_item_id))
    db.commit()

""" def search_media_items(db: Session, search_query: str, skip: int = 0, limit: int = 100, **kwargs) -> List[MediaItem] or None:
    query = db.query(MediaItem).filter(
        or_(MediaItem.title.ilike(f"%{search_query}%"), MediaItem.description.ilike(f"%{search_query}%"))
    )
    query = _filter_query_by_params(query, **kwargs)
    return query.offset(skip).limit(limit).all() """

""" def search_media_items(db: Session, search_query: str, skip: int = 0, limit: int = 100, **kwargs) -> List[MediaItem] or None:
    query = db.query(MediaItem).filter(
        or_(
            func.similarity(MediaItem.title, search_query) > 0.3,
            func.similarity(MediaItem.description, search_query) > 0.3
        )
    )
    query = _filter_query_by_params(query, **kwargs)
    return query.offset(skip).limit(limit).all() """

def search_media_items(db: Session, search_query: str, skip: int = 0, limit: int = 100, **kwargs) -> List[MediaItem] or None:
    # decode umlauts
    search_query = unidecode(search_query)
    # Transform the query to a tsquery-compatible string
    ts_query_str = " & ".join(search_query.split()) + ":*"
    ts_query = text("search_vector @@ to_tsquery(:query)").bindparams(query=ts_query_str)
    
    query = db.query(MediaItem).filter(ts_query)
    query = _filter_query_by_params(query, **kwargs)
    return query.offset(skip).limit(limit).all()

def get_all_media_items_by_topic(db: Session, topic: str, skip: int = 0, limit: int = 100, **kwargs) -> List[MediaItem] or None:
    topic = db.query(Topic).filter(Topic.name == topic).first()
    if not topic:
        return None
    topic_id = topic.id
    query = db.query(MediaItem).filter(MediaItem.topic_id == topic_id)
    query = _filter_query_by_params(query, **kwargs)
    #sort by date and time
    return query.order_by(MediaItem.date.desc(), MediaItem.time.desc()).offset(skip).limit(limit).all()

def like_media_item(db: Session, media_item_id: int) -> MediaItem:
    media_item = get_media_item(db, media_item_id)
    media_item.likes += 1
    db.commit()
    db.refresh(media_item)
    return media_item

def recommend_media_item(db: Session, media_item_id: int, user_id: int) -> bool:
    # check if recommendation already exists
    if(isRecommendedByUser(db, media_item_id, user_id)):
        print("Recommendation already exists, unrecommending...")
        unrecommend_media_item(db, media_item_id, user_id)
        return True
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    media_item = db.query(MediaItem).filter(MediaItem.id == media_item_id).first()
    if not media_item:
        return False
    recommendation = Recommendation(user_id=user_id, mediaitem_id=media_item_id, user=user, mediaitem=media_item)
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return True

def unrecommend_media_item(db: Session, media_item_id: int, user_id: int) -> None:
    db.query(Recommendation).filter(
        Recommendation.user_id == user_id,
        Recommendation.mediaitem_id == media_item_id
    ).delete()
    db.commit()

def isRecommendedByUser(db: Session, media_item_id: int, user_id: int) -> bool:
    recommendation = db.query(Recommendation).filter(
        Recommendation.user_id == user_id,
        Recommendation.mediaitem_id == media_item_id
    ).first()
    return bool(recommendation)

def get_recommended_media_items(db: Session, skip: int = 0, limit: int = 100, **kwargs) -> List[MediaItem]:
    query = db.query(MediaItem).join(Recommendation, Recommendation.mediaitem_id == MediaItem.id)
    query = _filter_query_by_params(query, **kwargs)
    return query.offset(skip).limit(limit).all()

def add_series_metadata(db: Session, series_metadata: schemas.MediaItemSeries) -> MediaItem:
    media_item = get_media_item(db, series_metadata.media_item_id)
    media_item.season_number = series_metadata.season_number if series_metadata.season_number != 0 else None
    media_item.episode_number = series_metadata.episode_number if series_metadata.episode_number != 0 else None
    media_item.series_name = series_metadata.series_name if series_metadata.series_name != "" else None
    db.commit()
    db.refresh(media_item)
    print(f"Added series metadata for {media_item.id}")
    return media_item

def get_all_series_items(db: Session, media_item_id: int) -> List[MediaItem]:
    media_item = get_media_item(db, media_item_id)
    if not media_item:
        return []
    if not media_item.series_name:
        return []
    
    # query all items which have the same series name
    query = db.query(MediaItem).filter(MediaItem.series_name == media_item.series_name)
    return query.all()


def get_thumbnail(db: Session, media_item_id: int) -> str:
    media_item = get_media_item(db, media_item_id)
    print(f"Getting thumbnail for {media_item.id}")
    if not media_item:
        return ""
    
    if not media_item.thumbnail or media_item.thumbnail == "":

        media_item.thumbnail = service.fetch_thumbnail(media_item.url)
        print(f"Thumbnail for {media_item.id} is {media_item.thumbnail}")
        db.commit()
        db.refresh(media_item)
        return media_item.thumbnail

def get_media_item_by_url(db: Session, url: str) -> MediaItem:
    return db.query(MediaItem).filter(MediaItem.url_website == url).first()
    
def get_first_episodes_of_all_series(db: Session, skip: int = 0, limit: int = 100, **kwargs) -> List[MediaItem]:
    # Subquery to find the minimum episode_number for each series
    # This identifies the first episode for each series
    subquery = (
        db.query(
            MediaItem.series_name,
            func.min(MediaItem.episode_number).label("min_episode_number")
        )
        .filter(MediaItem.series_name.isnot(None), MediaItem.episode_number.isnot(None))
        .group_by(MediaItem.series_name)
        .subquery()
    )
    
    # Main query joins with subquery to get details of the first episodes
    # The 'and_' is necessary for multiple join conditions
    query = (
        db.query(MediaItem)
        .join(
            subquery,
            and_(
                MediaItem.series_name == subquery.c.series_name,
                MediaItem.episode_number == subquery.c.min_episode_number
            )
        )
        # sort randomly if requested
        .order_by(func.random() if kwargs.get('random_order') else MediaItem.date.desc(), MediaItem.time.desc())
    )

    query = _filter_query_by_params(query, **kwargs)
    return query.offset(skip).limit(limit).all()

#get_all_media_items_by_ids(db, ids=ids, **common_params)
def get_all_media_items_by_ids(db: Session, str_ids: str, skip: int = 0, limit: int = 100, **kwargs) -> List[MediaItem]:
    ids = [int(id) for id in str_ids.split(",")]
    query = db.query(MediaItem).filter(MediaItem.id.in_(ids))
    query = _filter_query_by_params(query, **kwargs)
    fetched_items = query.offset(skip).limit(limit).all()

    # Create a dictionary with the fetched items, where the key is the item's ID.
    id_to_item = {item.id: item for item in fetched_items}

    # Reorder the fetched items according to the original list of IDs.
    # This ensures that the order of items in 'ordered_items' matches the order of IDs in 'ids'.
    ordered_items = [id_to_item[id] for id in ids if id in id_to_item]

    return ordered_items