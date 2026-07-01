"""Series detection job model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text

from ...core.db.database import Base


class SeriesDetectionJob(Base):
    """Tracks async series detection jobs."""
    __tablename__ = "series_detection_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source_video_id = Column(Integer, index=True, nullable=False)
    target_video_id = Column(Integer, index=True, nullable=False)
    state = Column(String, default="pending")  # pending | running | completed | failed
    result_json = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
