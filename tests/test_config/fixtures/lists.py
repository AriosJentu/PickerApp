
import pytest_asyncio

from app.shared.db.base import User, Algorithm, Lobby, Team, LobbyParticipant
from app.modules.auth.user.enums import UserRole

from tests.test_config.utils.constants import (
    USERS_COUNT, 
    ALGORITHMS_COUNT, 
    LOBBIES_COUNT, 
    TEAMS_COUNT,
    PARTICIPANTS_COUNT
)

from tests.test_config.factories.algorithm_factory import AlgorithmFactory
from tests.test_config.factories.lobby_factory import LobbyFactory
from tests.test_config.factories.participant_factory import ParticipantFactory
from tests.test_config.factories.team_factory import TeamFactory
from tests.test_config.factories.token_factory import TokenFactory
from tests.test_config.factories.user_factory import UserFactory

from tests.test_config.utils.user_utils import create_user_with_tokens


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