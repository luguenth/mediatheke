from fastapi import HTTPException, APIRouter
from . import service
from fastapi_cache.decorator import cache


from ..mediaitem import schemas
from . import service
from . import tasks

router = APIRouter(
    prefix="/thumbnail",
    tags=["Thumbnail"],
)


@router.get("/proxy/url", response_model=schemas.MediaItemUrl)
@cache()
def get_thumbnail(
        media_item_id: int,
        url: str
        ):
    """Gets the thumbnail for a media item."""
    # print whole path
    thumbnail_url = service.fetch_thumbnail(url)

    #persist thumbnail with celery task to not block the request
    if thumbnail_url is None or thumbnail_url == "":
        raise HTTPException(status_code=404, detail="MediaItem not found")
    tasks.persist_thumbnail.delay(media_item_id, thumbnail_url)
    return {"url": thumbnail_url, "media_item_id": media_item_id}

@router.get("/typesense")
def get_typesense_infos():
    return service.get_search_engine().get_debugging_info()

@router.get("/typesense/index")
def index_typesense():
    return service.get_search_engine().index_media_items()