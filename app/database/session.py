"""
NOTE: Since login/OAuth is already implemented in your project, this file (or an
equivalent) most likely already exists. Included here only for completeness so
this module is runnable standalone. If you already have `database/session.py`,
just make sure `get_db` and `Base` match this shape and skip this file.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config.settings import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a DB session and guarantees closing it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
