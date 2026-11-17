import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config.settings import settings

database_url = settings.database_url
connect_args = {}

if database_url.startswith("sqlite:///"):
    connect_args["check_same_thread"] = False
    db_path = database_url.replace("sqlite:///", "", 1)
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    database_url,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()