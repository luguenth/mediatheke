from ...core.db.database import get_db
from ..filmliste.model import FilmlisteImportEvent
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any

#return FilmlisteImportEvent or None
def get_last_full_import_event(db: Session = Depends(get_db)) -> Optional[FilmlisteImportEvent]:
    """Get last full import event"""
    return db.query(FilmlisteImportEvent).filter(FilmlisteImportEvent.full_import == True).order_by(FilmlisteImportEvent.timestamp.desc()).first()

def get_last_import_event(db: Session = Depends(get_db)) -> FilmlisteImportEvent:
    """Get last import event"""
    return db.query(FilmlisteImportEvent).order_by(FilmlisteImportEvent.timestamp.desc()).first()

def create_import_event(db: Session = Depends(get_db), timestamp: datetime = datetime.utcnow(), success: bool = False, full_import: bool = False, media_item_count: int = 0, media_item_diff_count: int = 0, media_item_diff_new_count: int = 0, media_item_diff_updated_count: int = 0, media_item_diff_deleted_count: int = 0) -> FilmlisteImportEvent:
    """Set import event"""
    #check if timestamp and "full_import" already exist
    db_import_event = db.query(FilmlisteImportEvent).filter(FilmlisteImportEvent.timestamp == timestamp, FilmlisteImportEvent.full_import == full_import).first()
    if db_import_event:
        return None

    db_import_event = FilmlisteImportEvent(
        timestamp=timestamp,
        success=success,
        full_import=full_import,
        media_item_count=media_item_count,
        media_item_diff_count=media_item_diff_count,
        media_item_diff_new_count=media_item_diff_new_count,
        media_item_diff_updated_count=media_item_diff_updated_count,
        media_item_diff_deleted_count=media_item_diff_deleted_count
        )
    db.add(db_import_event)
    db.commit()
    db.refresh(db_import_event)
    return db_import_event