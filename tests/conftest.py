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
from app.core.config import settings

from app.db.session import get_async_session
from app.db.base import Base, User, Algorithm, Lobby, Team, LobbyParticipant
from app.enums.user import UserRole

from tests.types import RouteBaseFixture
from tests.constants import (
    USERS_COUNT, 
    ALGORITHMS_COUNT, 
    LOBBIES_COUNT, 
    TEAMS_COUNT,
    PARTICIPANTS_COUNT
)
from tests.factories.user_factory import UserFactory
from tests.factories.algorithm_factory import AlgorithmFactory
from tests.factories.lobby_factory import LobbyFactory
from tests.factories.team_factory import TeamFactory
from tests.factories.token_factory import TokenFactory
from tests.factories.participant_factory import ParticipantFactory
from tests.factories.general_factory import GeneralFactory

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
def protected_route(request) -> RouteBaseFixture:
    return request.param


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


@pytest.fixture
def participant_factory(db_async: AsyncSession, user_factory: UserFactory) -> ParticipantFactory:
    return ParticipantFactory(db_async, user_factory)


@pytest_asyncio.fixture
async def test_algorithm(
        user_factory: UserFactory, 
        algorithm_factory: AlgorithmFactory, 
) -> Algorithm:
    
    user = await user_factory.create(suffix="algorithm")
    return await algorithm_factory.create(user, user.id)


@pytest.fixture
async def test_lobby(
        user_factory: UserFactory, 
        test_algorithm: Algorithm, 
        lobby_factory: LobbyFactory
) -> Lobby:
    user = await user_factory.create(suffix="lobby")
    return await lobby_factory.create(user, test_algorithm)

@pytest_asyncio.fixture
async def test_lobby_id(test_lobby: Lobby) -> int:
    return test_lobby.id


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
    
    users = []
    for i in range(USERS_COUNT):
        user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, prefix=f"testuser{i+1}")
        users.append((user, access_token))

    return users


@pytest_asyncio.fixture
async def create_test_algorithms(
        user_factory: UserFactory, 
        algorithm_factory: AlgorithmFactory,
) -> list[Algorithm]:
    
    user = await user_factory.create(suffix="algorithms")
    algorithms = []

    for i in range(ALGORITHMS_COUNT):
        algorithm = await algorithm_factory.create(user, i+1)
        algorithms.append(algorithm)

    return algorithms


@pytest_asyncio.fixture
async def create_test_lobbies(
        user_factory: UserFactory, 
        lobby_factory: LobbyFactory,
        test_algorithm: Algorithm
) -> list[Lobby]:
    
    user = await user_factory.create(suffix="lobbies")
    lobbies = []

    for i in range(LOBBIES_COUNT):
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
    
    user = await user_factory.create(suffix="teams")
    lobby = await lobby_factory.create(user, test_algorithm)
    teams = []

    for i in range(TEAMS_COUNT):
        team = await team_factory.create(lobby, i+1)
        teams.append(team)

    return teams


@pytest_asyncio.fixture
async def create_test_participants(
        participant_factory: ParticipantFactory,
        test_lobby: Lobby
) -> list[LobbyParticipant]:
    
    participants = []
    for i in range(PARTICIPANTS_COUNT):
        participant = await participant_factory.create(test_lobby, i+1)
        participants.append(participant)

    return participants


@pytest.fixture
def general_factory(
        db_async: AsyncSession,
        user_factory: UserFactory, 
        token_factory: TokenFactory,
        algorithm_factory: AlgorithmFactory, 
        lobby_factory: LobbyFactory,
        team_factory: TeamFactory,
        participant_factory: ParticipantFactory
):
    return GeneralFactory(db_async, user_factory, token_factory, algorithm_factory, lobby_factory, team_factory, participant_factory)
