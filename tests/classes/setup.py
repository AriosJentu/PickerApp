import pytest

from app.db.base import Algorithm, Lobby, Team
from app.enums.user import UserRole

from tests.types import InputData
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.factories.general_factory import GeneralFactory


class BaseTestSetup:

    @pytest.fixture
    async def base_user(self, general_factory: GeneralFactory, role: UserRole) -> BaseUserData:
        return await general_factory.create_base_user(role)
    
    @pytest.fixture
    async def base_user_other(self, general_factory: GeneralFactory, role_other: UserRole) -> BaseUserData:
        return await general_factory.create_base_user(role_other, prefix="otheruser")
    
    @pytest.fixture
    async def base_user_refresh(self, general_factory: GeneralFactory, role: UserRole) -> BaseUserData:
        return await general_factory.create_base_user(role, is_refresh_token=True)

    @pytest.fixture
    async def base_admin(self, general_factory: GeneralFactory) -> BaseUserData:
        return await general_factory.create_base_user(UserRole.ADMIN, prefix="adminuser")
    
    @pytest.fixture
    async def base_user_headers(self, base_user: BaseUserData) -> InputData:
        return base_user.headers
        
    @pytest.fixture
    async def algorithm(self, general_factory: GeneralFactory, base_user: BaseUserData, algorithm_exists: bool) -> BaseObjectData[Algorithm]:
        return await general_factory.create_conditional_algorithm(base_user.user, algorithm_exists)
    
    @pytest.fixture
    async def algorithm_other(self, general_factory: GeneralFactory, base_user_other: BaseUserData, algorithm_exists: bool) -> BaseObjectData[Algorithm]:
        return await general_factory.create_conditional_algorithm(base_user_other.user, algorithm_exists)

    @pytest.fixture
    async def lobby(self, general_factory: GeneralFactory, base_user: BaseUserData, lobby_exists: bool) -> BaseObjectData[Lobby]:
        return await general_factory.create_conditional_lobby(base_user.user, lobby_exists)
    
    @pytest.fixture
    async def lobby_other(self, general_factory: GeneralFactory, base_user_other: BaseUserData, lobby_exists: bool) -> BaseObjectData[Lobby]:
        return await general_factory.create_conditional_lobby(base_user_other.user, lobby_exists)

    @pytest.fixture
    async def team(self, general_factory: GeneralFactory, lobby: BaseObjectData[Lobby], team_exists: bool) -> BaseObjectData[Team]:
        return await general_factory.create_conditional_team(lobby.data, team_exists)
    
    @pytest.fixture
    async def team_other(self, general_factory: GeneralFactory, lobby_other: BaseObjectData[Lobby], team_exists: bool) -> BaseObjectData[Team]:
        return await general_factory.create_conditional_team(lobby_other.data, team_exists)
