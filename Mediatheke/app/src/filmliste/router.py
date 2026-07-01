"""Filmliste Router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from ...core.db.database import get_db
from ..filmliste import crud

router = APIRouter(
    prefix="/filmliste",
    tags=["Filmliste"],
)


class LastImportEvent(BaseModel):
    timestamp: Optional[datetime] = None
    full_import: Optional[bool] = None
    success: Optional[bool] = None

    class Config:
        from_attributes: bool = True


@router.get("/last-import", response_model=LastImportEvent)
def last_import(db: Session = Depends(get_db)):
    """Returns the most recent filmliste import event (diff or full).

    The stored timestamp is naive UTC; we attach +00:00 here so clients
    can render it in their own timezone.
    """
    event = crud.get_last_import_event(db)
    if event is None:
        return LastImportEvent()
    ts = event.timestamp
    if ts is not None and ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return LastImportEvent(
        timestamp=ts,
        full_import=event.full_import,
        success=event.success,
    )