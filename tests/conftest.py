import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.crud.crud_user import db_create_user
from app.core.security.password import get_password_hash
from app.core.config import settings
from app.db.session import get_async_session
from app.db.base import Base, User
from app.schemas.user import UserUpdate

load_dotenv()


TEST_DATABASE_URL_ASYNC = settings.DATABASE_URL_TEST_ASYNC
def get_engine_and_session_async(echo: bool = False):
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


@pytest_asyncio.fixture
async def client_async(db_async):
    async def override_get_async_session():
        return db_async
    
    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def default_user_data():
    return {
        "username": "defaultuser",
        "email": "defaultuser@example.com",
        "password": "SecurePassword1!"
    }


@pytest.fixture
def default_admin_data():
    return {
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "SecureAdminPassword1!",
        "role": 3
    }


@pytest.fixture
async def access_token(client_async, default_user_data):
    await client_async.post("/api/v1/auth/register", json=default_user_data)

    response: Response = await client_async.post("/api/v1/auth/login", data=default_user_data)
    assert response.status_code == 200, f"Login failed: {response.json()}"
    
    json_data = response.json()
    return json_data["access_token"]


@pytest.fixture
async def admin_access_token(client_async, db_async, default_admin_data):
    admin_user_create = UserUpdate(**default_admin_data)
    admin_user = User.from_create(admin_user_create, get_password_hash)
    await db_create_user(db_async, admin_user)

    response: Response = await client_async.post("/api/v1/auth/login", data=default_admin_data)
    assert response.status_code == 200, f"Login failed: {response.json()}"
    
    json_data = response.json()
    return json_data["access_token"]
