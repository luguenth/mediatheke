"""
Database Connector
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import settings
from sqlalchemy.engine.base import Engine

Base = declarative_base()


def get_db_url():
    """Returns the database url."""
    sqlalchemy_database_url = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
        settings.postgres_user,
        settings.postgres_password,
        settings.postgres_host,
        settings.postgres_port,
        settings.postgres_db
    )
    return sqlalchemy_database_url


def get_test_db_url():
    """Returns the database url."""
    sqlalchemy_database_url = 'sqlite:///./test.db'
    return sqlalchemy_database_url


def get_engine() -> Engine:
    """Creates a new database Session."""
    engine = create_engine(
        get_test_db_url() if settings.environment == "test" else get_db_url(),
        connect_args={"check_same_thread": False}
        if settings.environment == "test"
        else {},
    )

    return engine


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=get_engine()
    )


def get_db():
    """Creates a new database Session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_new_db_session():
    """Creates and returns a new database Session."""
    return SessionLocal()
