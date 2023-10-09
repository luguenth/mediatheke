"""MediaItem Router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi_cache.decorator import cache
import logging

from ...core.db.database import get_db
from ..authentication import service as auth
from ..search import service as search
from ..mediaitem import crud as mediaitem_crud
from ..mediaitem import schemas
from ..user.model import User, Recommendation
from ..services.recommendations import get_recommendation_engine, RecommendationEngine
from ..services.openai import run_conversation

class CommonQueryParams(BaseModel):
    skip: int = 0
    limit: int = 10
    random_order: bool = False
    with_thumbnail: bool = False
    longer_than: int = 0
    newer_than: int = 0

ttls = {
    "1_min": 60,
    "5_min": 60*5,
    "10_min": 60*10,
    "30_min": 60*30,
    "1_hour": 60*60,
    "6_hours": 60*60*6,
    "12_hours": 60*60*12,
    "1_day": 60*60*24,
    "1_week": 60*60*24*7,
    "1_month": 60*60*24*30,
    "1_year": 60*60*24*365
}

def common_parameters(
    params: CommonQueryParams = Depends()
) -> dict:
    return params.dict()

router = APIRouter(
    prefix="/mediaitems",
    tags=["MediaItems"],
)

@router.get("/", response_model=list[schemas.MediaItem])
@cache(expire=ttls["1_hour"])
def read_media_items(
        common_params: dict = Depends(common_parameters),
        db: Session = Depends(get_db)
        ):
    """Returns a list of media items."""
    media_items = mediaitem_crud.get_all_media_items(db, **common_params)
    return media_items

@router.get("/serie", response_model=list[schemas.MediaItem])
def read_all_media_items_series(
        media_item_id: int,
        db: Session = Depends(get_db)
        ):
    """Returns a list of media items."""
    media_items = mediaitem_crud.get_all_series_items(db, media_item_id)
    if media_items is None:
        raise HTTPException(status_code=404, detail="MediaItem not found")
    return media_items

@router.get("/series", response_model=list[schemas.MediaItem])
def read_media_items_series(
        common_params: dict = Depends(common_parameters),
        db: Session = Depends(get_db)
        ):
    """Returns a list of media items."""
    logging.info("Getting series")
    media_items = mediaitem_crud.get_first_episodes_of_all_series(db, **common_params)
    logging.info(f"Found {len(media_items)} series")
    if media_items is None:
        raise HTTPException(status_code=404, detail="MediaItem not found")
    return media_items

#text seach with the recommendation engine
@router.get("/search/recommended", response_model=list[schemas.MediaItem])
def recommendations_for_text(
    query: str,
    common_params: dict = Depends(common_parameters),
    rec_engine: RecommendationEngine = Depends(get_recommendation_engine)
    ):
    """Returns a list of recommended media items."""
    print("Getting recommendations for text", query)
    return rec_engine.get_recommendations_for_text(query, **common_params)

@router.get("/recommended", response_model=list[schemas.MediaItem])
#@cache(expire=ttls["1_hour"])
def get_recommended_media_items(
        common_params: dict = Depends(common_parameters),
        db: Session = Depends(get_db)
        ):
    """Returns a list of recommended media items."""
    media_items = mediaitem_crud.get_recommended_media_items(db, **common_params)
    return media_items

@router.get("/search", response_model=list[schemas.MediaItem])
def search_media_items(
        query: str,
        common_params: dict = Depends(common_parameters),
        db: Session = Depends(get_db),
        searchEngine: search.SearchEngine = Depends(search.get_search_engine)
        ):
    """Returns a list of media items."""
    media_items = searchEngine.search(query)

    return_items: list[schemas.MediaItem] = []
    for item in media_items['hits']:
        item = item['document']
        return_items.append(schemas.MediaItem(**item))
    return return_items


#${this.apiUrl.media}/ids?ids=123,456,789
@router.get("/ids", response_model=list[schemas.MediaItem])
def read_media_items_by_ids(
        ids: str,
        common_params: dict = Depends(common_parameters),
        db: Session = Depends(get_db)
        ):
    """Returns a list of media items."""
    media_items = mediaitem_crud.get_all_media_items_by_ids(db, str_ids=ids, **common_params)
    if media_items is None:
        raise HTTPException(status_code=404, detail="MediaItem not found")
    return media_items


@router.get("/topic/{topic}", response_model=list[schemas.MediaItem])
@cache(expire=ttls["1_day"])
def read_media_items_by_topic(
        topic: str,
        common_params: dict = Depends(common_parameters),
        db: Session = Depends(get_db)
        ):
    """Returns a list of media items."""
    media_items = mediaitem_crud.get_all_media_items_by_topic(db, topic=topic, **common_params)
    if media_items is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return media_items

@router.get("/{media_item_id}", response_model=schemas.MediaItem)
@cache(expire=ttls["1_day"])
def read_media_item(
        media_item_id: int,
        db: Session = Depends(get_db)
        ):
    """Returns a media item."""
    db_media_item = mediaitem_crud.get_media_item(db, media_item_id=media_item_id)
    if db_media_item is None:
        raise HTTPException(status_code=404, detail="MediaItem not found")
    return db_media_item

# From here on we need authentication
@router.post("/{media_item_id}/like", response_model=schemas.MediaItem)
def like_media_item(
        media_item_id: int,
        current_user: User = Depends(auth.get_current_user),
        db: Session = Depends(get_db)
        ):
    """Likes a media item."""
    db_media_item = mediaitem_crud.like_media_item(db, media_item_id=media_item_id)
    if db_media_item is None:
        raise HTTPException(status_code=404, detail="MediaItem not found")
    return db_media_item

@router.get("/{video_id}/recommended", response_model=list[schemas.MediaItem])
@cache(expire=ttls["1_day"])
def recommendations(
    video_id: int,
    common_params: dict = Depends(common_parameters),
    rec_engine: RecommendationEngine = Depends(get_recommendation_engine)
    ):
    """Returns a list of recommended media items."""
    return rec_engine.get_recommendations(video_id, **common_params)

@router.get("/{video_id}/isrecommended", response_model=bool)
def is_recommended(
    video_id: int,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
    ):
    """Returns if this item is recommended by the user."""
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    recommendation = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.mediaitem_id == video_id
    ).first()

    return bool(recommendation)

@router.post("/{video_id}/recommend", response_model=bool)
def recommend_media_item(
        video_id: int,
        current_user: User = Depends(auth.get_current_user),
        db: Session = Depends(get_db)
        ):
    """Recommends a media item."""
    recommendation = mediaitem_crud.recommend_media_item(db, media_item_id=video_id, user_id=current_user.id)
    if recommendation is False:
        raise HTTPException(status_code=404, detail="MediaItem not found")
    return True

@router.get("/{media_item_id}/mightbeaseries", response_model=list[schemas.MediaItem])
def might_be_a_series(
        media_item_id: int,
        db: Session = Depends(get_db),
        rec_engine: RecommendationEngine = Depends(get_recommendation_engine)
        ):
    """Gets 30 recommended media items, and asks ChatGPT to look which ones might be a series. It gives back a json with the possible series."""
    rec_items = rec_engine.get_recommendations(media_item_id, limit=30)
    if len(rec_items) == 0:
        raise HTTPException(status_code=404, detail="MediaItem not found")
    print("Getting possible series for", media_item_id, flush=True)
    media_items: list[schemas.MediaItemSeries] = run_conversation(rec_items)
    print("Got possible series for", media_item_id, flush=True)
    for media_item in media_items:
        print("Adding series metadata for", media_item.media_item_id, flush=True)
        mediaitem_crud.add_series_metadata(db, media_item)
    
    # get the media item again to get the updated data
    all_series= mediaitem_crud.get_all_series_items(db, media_item_id)
    return all_series
    
