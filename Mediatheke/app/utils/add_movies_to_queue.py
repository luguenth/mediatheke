from ..src.thumbnail.tasks import generate_thumbnail_ffmpeg
from ..db.database import get_new_db_session
from ..mediaitem.model import MediaItem
from ..user.user import Recommendation



db = get_new_db_session()

"""
def recommend_media_item(db: Session, media_item_id: int, user_id: int) -> bool:
    # check if recommendation already exists
    if(isRecommendedByUser(db, media_item_id, user_id)):
        print("Recommendation already exists, unrecommending...")
        unrecommend_media_item(db, media_item_id, user_id)
        return True
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    media_item = db.query(MediaItem).filter(MediaItem.id == media_item_id).first()
    if not media_item:
        return False
    recommendation = Recommendation(user_id=user_id, mediaitem_id=media_item_id, user=user, mediaitem=media_item)
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return True

"""
# get all mediaitems w/o thumbnail, limit to all movies which are recommended
mediaitems = db.query(MediaItem).filter(MediaItem.thumbnail == None).filter(MediaItem.id.in_([r.mediaitem_id for r in db.query(Recommendation).all()])).all()
mediaitems = db.query(MediaItem).filter(MediaItem.thumbnail == None).limit(10)

print(mediaitems)

# get the first one
for mediaitem in mediaitems:
    # Assuming mediaitem has a URL and an ID
    media_url = mediaitem.url
    output_filename = f"{mediaitem.id}.webp"
    print(media_url)
    generate_thumbnail_ffmpeg.delay(media_url, output_filename)