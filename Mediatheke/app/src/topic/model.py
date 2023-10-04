"""Topic Model

A topic can be assigned to a media item. It is used to group media items by topic. They are separated 
by channel. So if ard has a topic called "Tatort", zdf can also have a topic called "Tatort". This
is not a problem, because they are separated by channel.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from ...core.db.database import Base

# pylint: disable=too-few-public-methods
class Topic(Base):
    """Topic Class"""
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    isactive = Column(Boolean)
    ispublic = Column(Boolean)
    created = Column(DateTime, default=datetime.utcnow())
    updated = Column(DateTime, default=datetime.utcnow())

    def __repr__(self) -> str:
        return '<Topic %r>' % self.name
    
    def __str__(self) -> str:
        return f'{self.name}'

    @staticmethod
    def get_topic_name(session, topic_id: int) -> str:
        """Returns the topic name for a given topic id"""
        return session.query(Topic).filter_by(id=topic_id).first().name
    
    @staticmethod
    def get_topic_id(session, topic_name: str) -> int:
        """Returns the topic id for a given topic name"""
        id = session.query(Topic).filter_by(name=topic_name).first().id
        if id:
            return id
        else:
            return None
