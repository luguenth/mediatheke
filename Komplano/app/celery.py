# celery.py
from celery import Celery

app = Celery('Komplano', broker='redis://redis:6379/0')
app.conf.broker_url = 'redis://redis:6379/0'

app.conf.update({
    'result_backend': 'redis://redis:6379/0'
})

app.autodiscover_tasks([
    'app.src.services.tasks',
    'app.src.filmliste.tasks',
    'app.src.search.tasks'
    ], force=True)

#set broker_connection_retry_on_startup to True 
#to retry connecting to the broker if the connection fails on startup.

app.conf.broker_connection_retry = True
if __name__ == '__main__':
    app.start()

def start():
    app.start()