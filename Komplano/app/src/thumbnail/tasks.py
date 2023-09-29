# tasks.py or within services
import subprocess
#import cv2
from ...celery import app
from ..mediaitem import crud
from ...core.db.database import SessionLocal
from ..services import recommendations

@app.task()
def generate_thumbnail_ffmpeg(media_url, output_filename):
    cmd = [
        'ffmpeg',
        '-ss', '30',
        '-i', media_url,
        '-vf', 'scale=iw/2:ih/2',
        '-vframes', '1',
        '-y',
        '/app/images/' + output_filename
    ]
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print('Thumbnail generated at ./images/' + output_filename)
        return True
    else:
        print(f'Error generating thumbnail. Return code: {result.returncode}')
        return False

""" @app.task()
def generate_thumbnail_cv2(media_url, output_filename):
    desired_width = 320
    cap = cv2.VideoCapture(media_url)
    
    cap.set(cv2.CAP_PROP_POS_MSEC, 30000)
    success, image = cap.read()
    if success:
        height, width, _ = image.shape
        ratio = width / height
        desired_height = int(desired_width / ratio)
        resized_image = cv2.resize(image, (desired_width, desired_height))

        # Convert to RGB (removing the alpha channel if it exists)
        if resized_image.shape[2] == 4:
            resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGRA2BGR)

        # Save as WebP format with desired compression
        # The value range for compression is 0-100, where 100 is no compression (lossless) and 0 is highest compression (lossy).
        compression_quality = 70
        output_path = '/app/images/' + output_filename
        cv2.imwrite(output_path, resized_image, [cv2.IMWRITE_WEBP_QUALITY, compression_quality])
        
        print(f'Thumbnail generated at {output_path}')
        return True
    else:
        print('Error generating thumbnail.')
        return False """
    
@app.task()
def persist_thumbnail(media_item_id, thumbnail_url):
    db = SessionLocal()
    media_item = crud.get_media_item(db, media_item_id)
    if media_item is None:
        print(f'Could not find media item with id {media_item_id}')
        return False
    media_item.thumbnail = thumbnail_url
    db.commit()
    db.close()
    print(f'Persisted thumbnail for media item with id {media_item_id}')


@app.task()
def init_recommendations():
    print("Initializing Recommendations")
    recommendations.get_recommendation_engine()
    print("Finished initializing Recommendations")
