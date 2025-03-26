from typing import AsyncGenerator

import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

from app.shared.db.base import Base


TEST_DATABASE_URL_ASYNC = settings.DATABASE_URL_TEST_ASYNC
def get_engine_and_session_async(echo: bool = False) -> tuple[AsyncEngine, AsyncSession]:
    engine_async = create_async_engine(TEST_DATABASE_URL_ASYNC, echo=echo)
    SessionLocalAsync = sessionmaker(
        bind=engine_async, 
        class_=AsyncSession, 
        expire_on_commit=False,
    )
    return engine_async, SessionLocalAsync


@pytest_asyncio.fixture
async def db_async() -> AsyncGenerator[AsyncSession, None]:
    engine_async, SessionLocalAsync = get_engine_and_session_async(echo=False)
    async with engine_async.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocalAsync() as session:
        yield session

    async with engine_async.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
