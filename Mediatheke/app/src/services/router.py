"""Router for series detection jobs (debug endpoint)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from ...core.db.database import get_db
from ..services.models import SeriesDetectionJob
from ..services.tasks import detect_series_for_video
from ..services.recommendations import get_recommendation_engine, RecommendationEngine
from ..mediaitem import crud as mediaitem_crud


router = APIRouter(
    prefix="/series-detection",
    tags=["SeriesDetection"],
)


class JobOut(BaseModel):
    id: int
    source_video_id: int
    target_video_id: int
    state: str
    result_json: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes: bool = True


@router.post("/trigger/{video_id}", response_model=list[JobOut])
def trigger_series_detection(
    video_id: int,
    db: Session = Depends(get_db),
    rec_engine: RecommendationEngine = Depends(get_recommendation_engine),
):
    """Trigger series detection for the given video AND each of its
    recommended neighbours.  Skips videos that already have series
    metadata.  Each Celery task fetches its own recommendations via
    the API, avoiding a second RecommendationEngine in the worker.
    """
    target = mediaitem_crud.get_media_item(db, video_id)
    if not target:
        raise HTTPException(status_code=404, detail="MediaItem not found")

    rec_items = rec_engine.get_recommendations(video_id, limit=30)
    all_video_ids = [video_id] + [item.id for item in rec_items]

    jobs: list[SeriesDetectionJob] = []
    for vid in all_video_ids:
        # Skip if this video already has series data.
        vid_obj = mediaitem_crud.get_media_item(db, vid)
        if vid_obj and vid_obj.series_name:
            continue

        # Reuse existing pending/running job
        existing = (
            db.query(SeriesDetectionJob)
            .filter(
                SeriesDetectionJob.source_video_id == video_id,
                SeriesDetectionJob.target_video_id == vid,
                SeriesDetectionJob.state.in_(["pending", "running"]),
            )
            .first()
        )
        if existing:
            jobs.append(existing)
            continue

        job = SeriesDetectionJob(
            source_video_id=video_id,
            target_video_id=vid,
            state="pending",
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        jobs.append(job)

        detect_series_for_video.delay(video_id, vid)

    return jobs


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    source_video_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List series detection jobs, optionally filtered by source video."""
    query = db.query(SeriesDetectionJob).order_by(SeriesDetectionJob.created_at.desc())
    if source_video_id is not None:
        query = query.filter(SeriesDetectionJob.source_video_id == source_video_id)
    jobs = query.limit(100).all()
    return jobs


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a single series detection job by id."""
    job = db.query(SeriesDetectionJob).filter(SeriesDetectionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
