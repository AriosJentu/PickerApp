import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import AsyncGenerator, Callable, Awaitable

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
from app.crud.lobby.algorithm import db_create_algorithm
from app.crud.lobby.lobby import db_create_lobby

from app.db.session import get_async_session
from app.db.base import Base, User, Algorithm, Lobby
from app.schemas.auth.user import UserUpdate
from app.enums.user import UserRole


load_dotenv()

type UserData = dict[str, str | UserRole]
type AlgorithmData = dict[str, str | int]
type LobbyData = dict[str, str | int]
type CallableUser = Callable[[UserData], Awaitable[User]]
type CallableUserData = Callable[[str], UserData]
type CallableLobbyData = Callable[[int], Awaitable[LobbyData]]


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
def default_user_data() -> CallableUserData:
    def _generate_user_data(suffix: str = "") -> UserData:
        return {
            "username": f"defaultuser{suffix}",
            "email": f"defaultuser{suffix}@example.com",
            "password": "SecurePassword1!",
            "role": UserRole.USER
        }
    return _generate_user_data


@pytest.fixture
def default_moderator_data() -> CallableUserData:
    def _generate_user_data(suffix: str = "") -> UserData:
        return {
            "username": f"moderatoruser{suffix}",
            "email": f"moderator{suffix}@example.com",
            "password": "ModeratorPassword1!",
            "role": UserRole.MODERATOR
        }
    return _generate_user_data


@pytest.fixture
def default_admin_data() -> CallableUserData:
    def _generate_user_data(suffix: str = "") -> UserData:
        return {
            "username": f"adminuser{suffix}",
            "email": f"admin{suffix}@example.com",
            "password": "SecureAdminPassword1!",
            "role": UserRole.ADMIN
        }
    return _generate_user_data


@pytest.fixture
def test_user(db_async: AsyncSession) -> CallableUser:
    async def _generate_user(data: UserData):
        user_create = UserUpdate(**data)
        user = User.from_create(user_create, get_password_hash)
        return await db_create_user(db_async, user)
    return _generate_user


@pytest_asyncio.fixture
async def create_test_users(
        test_user: CallableUser,
        default_user_data: CallableUserData, 
        default_moderator_data: CallableUserData, 
        default_admin_data: CallableUserData
) -> list[User]:
    
    return [
        await test_user(default_user_data()), 
        await test_user(default_moderator_data()), 
        await test_user(default_admin_data())
    ]


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


@pytest.fixture
async def default_algorithm_data(
        test_user: CallableUser,
        default_user_data: CallableUserData, 
) -> AlgorithmData:
    user = await test_user(default_user_data("0"))
    return {
        "name": "Test Algorithm",
        "description": "Test algorithm for lobby",
        "algorithm": "BB PP T",
        "teams_count": 2,
        "creator_id": user.id
    }


@pytest.fixture
async def test_algorithm_id(db_async: AsyncSession, default_algorithm_data: AlgorithmData) -> int:
    algorithm = Algorithm(**default_algorithm_data)
    algorithm = await db_create_algorithm(db_async, algorithm)
    return algorithm.id


@pytest.fixture
def default_lobby_data(
        test_algorithm_id: int,
        test_user: CallableUser,
        default_user_data: CallableUserData
) -> CallableLobbyData:
    
    async def _generate_lobby_data(i: int = 1) -> LobbyData:
        user = await test_user(default_user_data(str(i)))
        return {
            "name": f"Test Lobby {i}",
            "description": f"Test Lobby {i} for API testing",
            "host_id": user.id,
            "algorithm_id": test_algorithm_id
        }
    
    return _generate_lobby_data


@pytest.fixture
async def test_lobby_id(db_async: AsyncSession, default_lobby_data: CallableLobbyData) -> int:
    lobby_data = await default_lobby_data(1)
    lobby = Lobby(**lobby_data)
    lobby = await db_create_lobby(db_async, lobby)
    return lobby.id


@pytest.fixture
async def create_test_lobbies(db_async: AsyncSession, default_lobby_data: CallableLobbyData) -> list[Lobby]:
    
    lobbies_count = 5
    lobbies = []
    
    for i in range(lobbies_count):
        lobby_data = await default_lobby_data(i+1)
        lobby = Lobby(**lobby_data)
        lobby = await db_create_lobby(db_async, lobby)
        lobbies.append(lobby)

    return lobbies
