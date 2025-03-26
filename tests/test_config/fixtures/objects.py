import pytest
import pytest_asyncio

from app.shared.db.base import Algorithm, Lobby

from tests.test_config.factories.algorithm_factory import AlgorithmFactory
from tests.test_config.factories.lobby_factory import LobbyFactory
from tests.test_config.factories.user_factory import UserFactory


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
