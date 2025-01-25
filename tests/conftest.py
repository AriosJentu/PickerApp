import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.security.user import create_user_tokens
from app.core.security.password import get_password_hash
from app.core.config import settings
from app.crud.auth.user import db_create_user
from app.db.session import get_async_session
from app.db.base import Base, User
from app.schemas.auth.user import UserUpdate
from app.enums.user import UserRole


load_dotenv()


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


@pytest_asyncio.fixture
async def client_async(db_async: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_async_session():
        return db_async
    
    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def default_user_data() -> dict[str, str | UserRole]:
    return {
        "username": "defaultuser",
        "email": "defaultuser@example.com",
        "password": "SecurePassword1!",
        "role": UserRole.USER
    }


@pytest.fixture
def default_moderator_data() -> dict[str, str | UserRole]:
    return {
        "username": "moderatoruser",
        "email": "moderator@example.com",
        "password": "ModeratorPassword1!",
        "role": UserRole.MODERATOR
    }


@pytest.fixture
def default_admin_data() -> dict[str, str | UserRole]:
    return {
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "SecureAdminPassword1!",
        "role": UserRole.ADMIN
    }


@pytest_asyncio.fixture
async def create_test_users(
        db_async: AsyncSession,
        default_user_data: dict[str, str | UserRole], 
        default_moderator_data: dict[str, str | UserRole], 
        default_admin_data: dict[str, str | UserRole]
) -> list[User]:
    
    users = [default_user_data, default_moderator_data, default_admin_data]

    user_objects = []
    for user_data in users:
        user_create = UserUpdate(**user_data)
        user = User.from_create(user_create, get_password_hash)
        await db_create_user(db_async, user)
        user_objects.append(user)

    return user_objects


@pytest_asyncio.fixture
async def user_access_token(db_async: AsyncSession, create_test_users: list[User]) -> str:
    regular_user = next(user for user in create_test_users if user.role == UserRole.USER)
    access_token, _ = await create_user_tokens(db_async, regular_user)
    return access_token.token


@pytest_asyncio.fixture
async def moderator_access_token(db_async: AsyncSession, create_test_users: list[User]):
    moderator_user = next(user for user in create_test_users if user.role == UserRole.MODERATOR)
    access_token, _ = await create_user_tokens(db_async, moderator_user)
    return access_token.token


@pytest_asyncio.fixture
async def admin_access_token(db_async: AsyncSession, create_test_users: list[User]) -> str:
    admin_user = next(user for user in create_test_users if user.role == UserRole.ADMIN)
    access_token, _ = await create_user_tokens(db_async, admin_user)
    return access_token.token
