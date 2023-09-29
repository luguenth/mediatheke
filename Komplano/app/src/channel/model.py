"""Channel model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from ...core.db.database import Base

# pylint: disable=too-few-public-methods
class Channel(Base):
    """Channel Class"""
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    website = Column(String)
    isactive = Column(Boolean)
    ispublic = Column(Boolean)
    created = Column(DateTime, default=datetime.utcnow())
    updated = Column(DateTime, default=datetime.utcnow())

    def __repr__(self) -> str:
        return '<Channel %r>' % self.name
    
    def __str__(self) -> str:
        return f'{self.name}'
    
    @staticmethod
    def get_channel_name(session, channel_id: int) -> str:
        """Returns the channel name for a given channel id"""
        return session.query(Channel).filter_by(id=channel_id).first().name
    
    @staticmethod
    def get_channel_id(session, channel_name: str) -> int:
        """Returns the channel id for a given channel name"""
        id = session.query(Channel).filter_by(name=channel_name).first().id
        if id:
            return id
        else:
            return None
    

