"""Main Module"""
import subprocess
import asyncio

from redis import asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from dotenv import load_dotenv

from .src.user import router as user_router
from .src.authentication import router as auth_router
from .src.mediaitem import router as mediaitem_router
from .src.thumbnail import router as thumbnail_router

from .src.thumbnail import tasks as thumbnail_tasks
from .src.filmliste import tasks as filmliste_tasks
from .src.search import tasks as search_tasks

from .core.db.database import Base, get_engine
from .core.config import get_settings

from .celery import start as celery_app

load_dotenv()


app = FastAPI(
    title="mediatheke.org API",
    description="Die API für mediatheke.org, eine Plattform für die Sammlung von Medieninhalten aus den Mediatheken der öffentlich-rechtlichen Sender. Einen großen Dank an die Macher von mediathekviewweb.de, die die Daten zur Verfügung stellen. \n\nDie API ist noch in der Entwicklung und wird ständig erweitert. Aktuell gibt es noch keinen Index und keine Caches. \n\nDie Dokumentation ist unter https://mediatheke.org/api/docs zu finden.",
    version="0.1.0",
)

#app.mount("/images", StaticFiles(directory="/app/images"), name="images")

app.add_middleware(GZipMiddleware, minimum_size=100)

origins = [
    "http://localhost",
    "http://localhost:4200",
    "http://localhost:8000",
    "http://server",
    "http://server:8000",
    "https://mediatheke.org",
    "https://www.mediatheke.org",
    "http://client",
    "http://client:4200",
]

if get_settings().environment != "test":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

Base.metadata.create_all(bind=get_engine())

# app.include_router(user_router.router)
app.include_router(auth_router.router)
app.include_router(mediaitem_router.router)
app.include_router(thumbnail_router.router)


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url("redis://redis")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    # start the celery worker
    subprocess.Popen(["pipenv", "run", "celery", "-A", "app.celery", "worker", "--loglevel=info"])
    
    # we have to wait for the celery worker to start up
    print("Waiting for celery worker to start up...", flush=True)
    print(filmliste_tasks.import_filmliste.delay())
    print(search_tasks.init_typesense.delay())

@app.on_event("shutdown")
async def shutdown_event():
    # shutdown the celery worker
    subprocess.Popen(["pkill", "-f", "celery"])
    print("Celery worker shut down")