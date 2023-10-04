"""Media Item model."""
from sqlalchemy import Column, Integer, String, Date, Time, Float, UniqueConstraint

from ...core.db.database import Base



# pylint: disable=too-few-public-methods
class MediaItem(Base):
    """Media Item Class"""
    __tablename__ = 'mediaitems'
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, index=True)
    topic_id = Column(Integer, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    date = Column(Date)
    time = Column(Time)
    duration = Column(Integer)
    size_MB = Column(Float)
    url_website = Column(String)
    url_subtitle = Column(String)
    url_video = Column(String)
    url_video_descriptive_audio = Column(String, nullable=True)
    url_video_low = Column(String)
    url_video_low_descriptive_audio = Column(String, nullable=True)
    url_video_hd = Column(String)
    url_video_hd_descriptive_audio = Column(String, nullable=True)
    timestamp = Column(String)
    thumbnail = Column(String)

    episode_number = Column(Integer, nullable=True)
    season_number = Column(Integer, nullable=True)
    series_name = Column(String, nullable=True)

    import_event_id = Column(Integer, index=True)

    channel = Column(String)
    topic = Column(String)

    # make website and the timestamp unique
    __table_args__ = (UniqueConstraint('url_website', 'timestamp', name='website_timestamp_unique'),)

    def __repr__(self):
        return f'<MediaItem {self.title}>'
    
    def __str__(self):
        return f'{self.title}'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'topic_id': self.topic_id,
            'title': self.title,
            'date': self.date,
            'duration': self.duration,
            'size_MB': self.size_MB,
            'description': self.description,
            'url': self.url,
            'website': self.website,
            'subtitle_url': self.subtitle_url,
            'rtmp_url': self.rtmp_url,
            'small_url': self.small_url,
            'small_rtmp_url': self.small_rtmp_url,
            'hd_url': self.hd_url,
            'hd_rtmp_url': self.hd_rtmp_url,
            'timestamp': self.timestamp,
            'history_url': self.history_url,
            'geo': self.geo,
            'is_new': self.is_new,
            'channel': self.channel,
            'topic': self.topic,
            'thumbnail': self.thumbnail
        }