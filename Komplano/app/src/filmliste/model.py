"""
Filmliste Model.

Here we define Metadata over the current "Filmliste".
The Filmliste contains all the MediaItems that are available in the Database. 
There is alawys a "Filmliste" and a "Filmliste-diff" which contains the changes to the Filmliste.
So we need to know, when the last change to the Filmliste was made. The diff gets updated every hour.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from ...core.db.database import Base

class FilmlisteImportEvent(Base):
    """Filmliste Import Events Class"""
    __tablename__ = 'filmliste_import_events'
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow())
    message = Column(String)
    success = Column(Boolean, default=False)
    full_import = Column(Boolean, default=False)
    media_item_count = Column(Integer, default=0)
    media_item_diff_count = Column(Integer, default=0)
    media_item_diff_new_count = Column(Integer, default=0)
    media_item_diff_updated_count = Column(Integer, default=0)
    media_item_diff_deleted_count = Column(Integer, default=0)

    def __repr__(self):
        return f'<FilmlisteImportEvent {self.id}>'
    
    def __str__(self):
        return f'{self.id}'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
