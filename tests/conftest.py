import os
import pytest
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base

load_dotenv()

TEST_DATABASE_URL = settings.DATABASE_URL_TEST_SYNC
engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()

    Base.metadata.drop_all(bind=engine)
