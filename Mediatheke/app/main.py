"""Main Module"""
import asyncio

from redis import asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from dotenv import load_dotenv

from .src.user import router as user_router
from .src.authentication import router as auth_router
from .src.mediaitem import router as mediaitem_router
from .src.thumbnail import router as thumbnail_router
from .src.services import router as services_router
from .src.filmliste import router as filmliste_router
from .src.oidc import router as oidc_router

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
app.add_middleware(SessionMiddleware, secret_key=get_settings().secret_key)

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
app.include_router(services_router.router)
app.include_router(filmliste_router.router)
app.include_router(oidc_router.router)


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url("redis://redis")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    # enqueue initial tasks; the worker container picks them up from Redis
    print(filmliste_tasks.check_for_updates.delay())
    print(search_tasks.init_typesense.delay())
    # Load recommendation engine synchronously in the web process
    from .src.services.recommendations import get_recommendation_engine
    engine = get_recommendation_engine()
    engine.load()
    print("Recommendation engine loaded", flush=True)