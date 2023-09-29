from ..filmliste.parser_old import FilmlisteParser
from ..mediaitem.crud import process_batch
from ..db.database import get_new_db_session
from .progressbar import display_progress_bar

BATCH_SIZE = 1000

def populate_database():
    items = FilmlisteParser.getFilms("Filmliste-akt")
    total_items = len(items)

    db = get_new_db_session()
    db.autocommit = False
    db.autoflush = False

    for i in range(0, total_items, BATCH_SIZE):
        batch = items[i:i + BATCH_SIZE]
        process_batch(db, batch)
        # Displaying progress every batch can be useful
        display_progress_bar(min(i + BATCH_SIZE, total_items), total_items)
    
    db.close()
    print()  # Move to the next line after completion


def create_one_test_media_item():
    """This is just for testing the database Connection"""
    test_item = {
        'channel': 'ARD',
        'topic': 'Doku',
        'title': 'Test',
        'date': '2020-01-01',
        'time': '12:00:00',
        'duration': 3600,
        'size_MB': 100,
        'description': 'Test',
        'url': 'https://www.ardmediathek.de/ard/video/doku-und-reportage/der-erste-weltkrieg-der-krieg-der-die-welt-veraenderte/ard-alpha/Y3JpZDovL2JyLmRlL3ZpZGVvLzEwMjUxNjQ2/',
        'website': 'https://www.ardmediathek.de/ard/video/doku-und-reportage/der-erste-weltkrieg-der-krieg-der-die-welt-veraenderte/ard-alpha/Y3JpZDovL2JyLmRlL3ZpZGVvLzEwMjUxNjQ2/',
        'subtitle_url': 'https://www.ardmediathek.de/ard/subtitle/10251646',
        'rtmp_url': 'rtmp://fms.105.net:1935/105tv',
        'small_url': 'https://www.ardmediathek.de/ard/video/doku-und-reportage/der-erste-weltkrieg-der-krieg-der-die-welt-veraenderte/ard-alpha/Y3JpZDovL2JyLmRlL3ZpZGVvLzEwMjUxNjQ2/',
        'small_rtmp_url': 'rtmp://fms.105.net:1935/105tv',
        'hd_url': 'https://www.ardmediathek.de/ard/video/doku-und-reportage/der-erste-weltkrieg-der-krieg-der-die-welt-veraenderte/ard-alpha/Y3JpZDovL2JyLmRlL3ZpZGVvLzEwMjUxNjQ2/',
        'hd_rtmp_url': 'rtmp://fms.105.net:1935/105tv',
        'timestamp': '2020-01-01T12:00:00+01:00',
        'history_url': 'https://www.ardmediathek.de/ard/servlet/ajax-cache/3618/histories/10251646',
        'geo': 'DE',
        'is_new': True
    }

    db = get_new_db_session()
    
    get_or_create_media_item(db, test_item)

    db.close()




    

if __name__ == "__main__":
    populate_database()
    #create_one_test_media_item()