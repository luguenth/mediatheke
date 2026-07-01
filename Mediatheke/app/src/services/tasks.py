"""Celery tasks for series detection."""
import json
import logging
from datetime import datetime

import requests

from ...celery import app
from ...core.db.database import get_new_db_session
from ..mediaitem import crud as mediaitem_crud
from .openai import run_conversation
from .models import SeriesDetectionJob

_RECOMMENDATIONS_URL = "http://127.0.0.1:8000/mediaitems/{video_id}/recommended?limit=30"


@app.task(bind=True, max_retries=2, default_retry_delay=30)
def detect_series_for_video(self, source_video_id: int, target_video_id: int):
    """Detect series metadata for a video and its 30 nearest neighbours.

    Gets recommendations by calling the existing FastAPI endpoint internally
    (avoids loading the full RecommendationEngine into the Celery worker).
    """
    db = get_new_db_session()
    try:
        job = _get_or_create_job(db, source_video_id, target_video_id)
        job.state = "running"
        db.commit()

        target = mediaitem_crud.get_media_item(db, target_video_id)
        if not target:
            job.state = "failed"
            job.error = f"MediaItem {target_video_id} not found"
            job.completed_at = datetime.utcnow()
            db.commit()
            return

        rec_ids = _fetch_recommended_ids(target_video_id)
        all_ids = [target_video_id] + rec_ids

        candidates = [
            mediaitem_crud.get_media_item(db, cid) for cid in all_ids
        ]
        candidates = [c for c in candidates if c is not None]

        if target not in candidates:
            candidates.insert(0, target)

        logging.info(
            "Detecting series for video %s (source %s) with %d candidates",
            target_video_id, source_video_id, len(candidates),
        )
        results = run_conversation(candidates)

        for item in results:
            mediaitem_crud.add_series_metadata(db, item)

        job.state = "completed"
        job.result_json = json.dumps(
            [
                {
                    "media_item_id": r.media_item_id,
                    "title": r.title,
                    "episode_number": r.episode_number,
                    "season_number": r.season_number,
                    "series_name": r.series_name,
                }
                for r in results
            ],
            default=str,
        )
        job.completed_at = datetime.utcnow()
        db.commit()

        logging.info(
            "Series detection completed for video %s: %d results",
            target_video_id, len(results),
        )

    except Exception as exc:
        logging.error("Series detection failed for video %s: %s", target_video_id, exc)
        try:
            job = (
                db.query(SeriesDetectionJob)
                .filter(
                    SeriesDetectionJob.source_video_id == source_video_id,
                    SeriesDetectionJob.target_video_id == target_video_id,
                )
                .order_by(SeriesDetectionJob.created_at.desc())
                .first()
            )
            if job:
                job.state = "failed"
                job.error = str(exc)
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception:
            db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()


def _fetch_recommended_ids(video_id: int) -> list[int]:
    """Call the existing recommendations endpoint and return IDs."""
    url = _RECOMMENDATIONS_URL.format(video_id=video_id)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    items = resp.json()
    # The endpoint returns a JSON array of MediaItem objects with 'id'.
    return [item["id"] for item in items if "id" in item]


def _get_or_create_job(db, source_video_id: int, target_video_id: int) -> SeriesDetectionJob:
    """Return an existing pending job for this pair, or create a new one."""
    job = (
        db.query(SeriesDetectionJob)
        .filter(
            SeriesDetectionJob.source_video_id == source_video_id,
            SeriesDetectionJob.target_video_id == target_video_id,
            SeriesDetectionJob.state == "pending",
        )
        .first()
    )
    if not job:
        job = SeriesDetectionJob(
            source_video_id=source_video_id,
            target_video_id=target_video_id,
            state="pending",
        )
        db.add(job)
        db.commit()
        db.refresh(job)
    return job
