from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional, Union

class MediaItemBase(BaseModel):
    channel: Optional[str]
    topic: Optional[str]
    title: str
    date: Optional[date]
    time: Optional[time]
    duration: Optional[int]
    size_MB: Optional[int]
    description: Optional[str]
    url_video: Optional[str]
    url_video_hd: Optional[str]
    url_video_low: Optional[str]
    url_video_descriptive_audio: Optional[str]
    url_video_hd_descriptive_audio: Optional[str]
    url_video_low_descriptive_audio: Optional[str]
    url_website: Optional[str]
    thumbnail: Optional[str]
    url_subtitle: Optional[str]
    episode_number: Optional[int]
    season_number: Optional[int]
    series_name: Optional[str]
    is_recommended: Optional[bool] = False

class MediaItemSeries(BaseModel):
    media_item_id: Optional[int]
    title: Optional[str]
    episode_number: Optional[int]
    season_number: Optional[int]
    series_name: Optional[str]

class MediaItemCreate(MediaItemBase):
    pass

class MediaItemUpdate(MediaItemBase):
    pass

class MediaItemInDBBase(MediaItemBase):
    id: int

    class Config:
        from_attributes: bool = True

class MediaItem(MediaItemInDBBase):
    pass

class MediaItemUrl(BaseModel):
    media_item_id: int
    url: str


# schema for typesense  
mediaitem_typesense_schema = {
    'name': 'mediaitems',
    'fields': [
        {'name': 'id', 'type': 'string'},
        {'name': 'channel', 'type': 'string'},
        {'name': 'topic', 'type': 'string'},
        {'name': 'title', 'type': 'string'},
        {'name': 'date', 'type': 'string'},
        {'name': 'time', 'type': 'string'},
        {'name': 'duration', 'type': 'int32'},
        {'name': 'size_MB', 'type': 'float'},
        {'name': 'description', 'type': 'string'},
        {'name': 'url_video', 'type': 'string'},
        {'name': 'url_website', 'type': 'string'},
        {'name': 'url_subtitle', 'type': 'string'},
        {'name': 'url_video_low', 'type': 'string'},
        {'name': 'url_video_hd', 'type': 'string'},
        {'name': 'thumbnail', 'type': 'string'},
        {'name': 'episode_number', 'type': 'int32'},
        {'name': 'season_number', 'type': 'int32'},
        {'name': 'series_name', 'type': 'string'},
    ]
}