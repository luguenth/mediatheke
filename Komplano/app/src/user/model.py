"""User Class Module"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ...core.db.database import Base

from ..mediaitem.model import MediaItem


# pylint: disable=too-few-public-methods
class User(Base):
    """User Class"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    displayname = Column(String)
    created = Column(DateTime, default=datetime.utcnow())
    isactive = Column(Boolean)
    role_id = Column(Integer, ForeignKey('roles.id'))

    role = relationship("Role", back_populates="users")
    
class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

Role.users = relationship('User', order_by=User.id, back_populates='role')

class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    mediaitem_id = Column(Integer, ForeignKey('mediaitems.id'))

    user = relationship("User", back_populates="recommendations")
    mediaitem = relationship("MediaItem", back_populates="recommendations")

User.recommendations = relationship('Recommendation', order_by=Recommendation.id, back_populates='user')
MediaItem.recommendations = relationship('Recommendation', order_by=Recommendation.id, back_populates='mediaitem')