# celery.py
from celery import Celery
from celery.schedules import crontab

print("Initializing celery app", flush=True)
app = Celery('Mediatheke', broker='redis://redis:6379/0')
app.conf.broker_url = 'redis://redis:6379/0'

app.conf.update({
    'result_backend': 'redis://redis:6379/0'
})

app.autodiscover_tasks([
    'app.src.services.tasks',
    'app.src.filmliste.tasks',
    'app.src.search.tasks',
    'app.src.thumbnail.tasks'
    ], force=True)

#set broker_connection_retry_on_startup to True 
#to retry connecting to the broker if the connection fails on startup.

app.conf.broker_connection_retry = True


app.conf.beat_schedule = {
    'check-for-updates': {
        'task': 'app.src.filmliste.tasks.check_for_updates',
        'schedule': crontab(minute=0),  # Run every hour
    },
}



if __name__ == '__main__':
    app.start()

def start():
    app.start()