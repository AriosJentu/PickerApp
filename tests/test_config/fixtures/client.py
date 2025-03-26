from typing import AsyncGenerator

import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from httpx import ASGITransport, AsyncClient

from app.main import app

from app.dependencies.database import get_async_session


@pytest_asyncio.fixture
async def client_async(db_async: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_async_session():
        return db_async
    
    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
