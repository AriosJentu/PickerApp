import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine

from app.core.config import settings
from app.db.base import Base


load_dotenv()

TEST_DATABASE_URL = settings.DATABASE_URL_TEST_SYNC
engine = create_engine(TEST_DATABASE_URL)


def init_test_db():
    print("Creating tables in test database...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")


if __name__ == "__main__":
    init_test_db()
