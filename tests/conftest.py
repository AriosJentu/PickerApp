import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import AsyncGenerator, Callable, Awaitable, Optional

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
from app.crud.lobby.team import db_create_team

from app.db.session import get_async_session
from app.db.base import Base, User, Algorithm, Lobby, Team
from app.schemas.auth.user import UserUpdate
from app.enums.user import UserRole
from app.enums.lobby import LobbyParticipantRole

from tests.factories.user_factory import UserFactory
from tests.factories.algorithm_factory import AlgorithmFactory
from tests.factories.lobby_factory import LobbyFactory
from tests.factories.team_factory import TeamFactory
from tests.factories.token_factory import TokenFactory

from tests.utils.user_utils import create_user_with_tokens


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
def user_factory(db_async: AsyncSession) -> UserFactory:
    return UserFactory(db_async)


@pytest.fixture
def algorithm_factory(db_async: AsyncSession) -> AlgorithmFactory:
    return AlgorithmFactory(db_async)


@pytest.fixture
def lobby_factory(db_async: AsyncSession) -> LobbyFactory:
    return LobbyFactory(db_async)


@pytest.fixture
def team_factory(db_async: AsyncSession) -> TeamFactory:
    return TeamFactory(db_async)


@pytest.fixture
def token_factory(db_async: AsyncSession) -> TokenFactory:
    return TokenFactory(db_async)


@pytest_asyncio.fixture
async def test_algorithm(
        user_factory: UserFactory, 
        algorithm_factory: AlgorithmFactory, 
) -> Algorithm:
    
    user = await user_factory.create(suffix="algorithm")
    return await algorithm_factory.create(user)


@pytest_asyncio.fixture
async def test_algorithm_id(
        test_algorithm: Algorithm, 
) -> int:
    return test_algorithm.id


@pytest.fixture
async def test_lobby(
        user_factory: UserFactory, 
        algorithm_factory: AlgorithmFactory, 
        lobby_factory: LobbyFactory
) -> Lobby:
    user = await user_factory.create(suffix="lobby")
    algorithm = await algorithm_factory.create(user)
    return await lobby_factory.create(user, algorithm)

@pytest_asyncio.fixture
async def test_lobby_id(test_lobby: Lobby) -> int:
    return test_lobby.id


@pytest.fixture
async def test_team(
        team_factory: TeamFactory, 
        test_lobby: Lobby
) -> Team:
    return await team_factory.create(test_lobby)


@pytest_asyncio.fixture
async def test_team_id(test_team: Team) -> int:
    return test_team.id


@pytest_asyncio.fixture
async def create_test_users(user_factory: UserFactory) -> list[User]:
    return [
        await user_factory.create(prefix="default",     role=UserRole.USER),
        await user_factory.create(prefix="moderator",   role=UserRole.MODERATOR),
        await user_factory.create(prefix="admin",       role=UserRole.ADMIN),
    ]


@pytest_asyncio.fixture
async def create_multiple_test_users_with_tokens(
        user_factory: UserFactory, 
        token_factory: TokenFactory
) -> list[tuple[User, str]]:
    
    users_count = 3
    users = []
    for i in range(users_count):
        user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, prefix=f"testuser{i+1}")
        users.append((user, access_token))

    return users


@pytest_asyncio.fixture
async def create_test_lobbies(
        user_factory: UserFactory, 
        lobby_factory: LobbyFactory,
        test_algorithm: Algorithm
) -> list[Lobby]:
    
    lobbies_count = 5
    user = await user_factory.create(suffix="lobbies")
    lobbies = []

    for i in range(lobbies_count):
        lobby = await lobby_factory.create(user, test_algorithm, i+1)
        lobbies.append(lobby)

    return lobbies


@pytest_asyncio.fixture
async def create_test_teams(
        user_factory: UserFactory, 
        lobby_factory: LobbyFactory,
        team_factory: TeamFactory,
        test_algorithm: Algorithm
) -> list[Team]:
    
    teams_count = 5
    user = await user_factory.create(suffix="teams")
    lobby = await lobby_factory.create(user, test_algorithm)
    teams = []

    for i in range(teams_count):
        team = await team_factory.create(lobby, i+1)
        teams.append(team)

    return teams
