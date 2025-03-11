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
    async def base_user_creator(self, general_factory: GeneralFactory, role: UserRole) -> tuple[BaseUserData, ...]:
        return await general_factory.create_base_users_creator(role)

    @pytest.fixture
    async def base_user_creator_additional(self, general_factory: GeneralFactory, role: UserRole) -> tuple[BaseUserData, ...]:
        return await general_factory.create_base_users_creator_aditional(role)
    
    @pytest.fixture
    async def base_user_headers(self, base_user: BaseUserData) -> InputData:
        return base_user.headers
        
    @pytest.fixture
    async def algorithm(self, general_factory: GeneralFactory, base_user: BaseUserData, algorithm_exists: bool) -> BaseObjectData[Algorithm]:
        return await general_factory.create_conditional_algorithm(base_user.user, algorithm_exists)  

    @pytest.fixture
    async def lobby(self, general_factory: GeneralFactory, base_user_creator: tuple[BaseUserData, ...], lobby_exists: bool) -> BaseObjectData[Lobby]:
        creator = base_user_creator[1].user
        return await general_factory.create_conditional_lobby(creator, lobby_exists)

    @pytest.fixture
    async def team(self, general_factory: GeneralFactory, lobby: BaseObjectData[Lobby], team_exists: bool) -> BaseObjectData[Team]:
        return await general_factory.create_conditional_team(lobby.data, team_exists)
