import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_config.factories.algorithm_factory import AlgorithmFactory
from tests.test_config.factories.general_factory import GeneralFactory
from tests.test_config.factories.lobby_factory import LobbyFactory
from tests.test_config.factories.participant_factory import ParticipantFactory
from tests.test_config.factories.team_factory import TeamFactory
from tests.test_config.factories.token_factory import TokenFactory
from tests.test_config.factories.user_factory import UserFactory


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
