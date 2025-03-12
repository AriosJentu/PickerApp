import pytest

from app.db.base import Algorithm, Lobby, LobbyParticipant, Team
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
        return await general_factory.create_conditional_algorithm(base_user.user, algorithm_exists, 1)
    
    @pytest.fixture
    async def algorithm_other(self, general_factory: GeneralFactory, base_user_other: BaseUserData, algorithm_exists: bool) -> BaseObjectData[Algorithm]:
        return await general_factory.create_conditional_algorithm(base_user_other.user, algorithm_exists, 2)

    @pytest.fixture
    async def lobby(self, general_factory: GeneralFactory, base_user: BaseUserData, lobby_exists: bool) -> BaseObjectData[Lobby]:
        return await general_factory.create_conditional_lobby(base_user.user, lobby_exists, 1)
    
    @pytest.fixture
    async def lobby_other(self, general_factory: GeneralFactory, base_user_other: BaseUserData, lobby_exists: bool) -> BaseObjectData[Lobby]:
        return await general_factory.create_conditional_lobby(base_user_other.user, lobby_exists, 2)

    @pytest.fixture
    async def team(self, general_factory: GeneralFactory, lobby: BaseObjectData[Lobby], team_exists: bool) -> BaseObjectData[Team | bool]:
        if lobby.data:
            return await general_factory.create_conditional_team(lobby.data, team_exists, 1)
        return BaseObjectData(-1, True)

    @pytest.fixture
    async def team_other(self, general_factory: GeneralFactory, lobby_other: BaseObjectData[Lobby], team_exists: bool) -> BaseObjectData[Team | bool]:
        if lobby_other.data:
            return await general_factory.create_conditional_team(lobby_other.data, team_exists, 2)
        return BaseObjectData(-1, True)
    
    @pytest.fixture
    async def participant(self, general_factory: GeneralFactory, lobby: BaseObjectData[Lobby], participant_exists: bool) -> BaseObjectData[LobbyParticipant]:
        if lobby.data:
            return await general_factory.create_conditional_participant(lobby.data, participant_exists, 1)
        return BaseObjectData(-1, True)
    
    @pytest.fixture
    async def participant_other(self, general_factory: GeneralFactory, lobby: BaseObjectData[Lobby], participant_exists: bool) -> BaseObjectData[LobbyParticipant]:
        if lobby.data:
            return await general_factory.create_conditional_participant(lobby.data, participant_exists, 2)
        return BaseObjectData(-1, True)
    
    @pytest.fixture
    async def participant_lobby_other(self, general_factory: GeneralFactory, lobby_other: BaseObjectData[Lobby], participant_exists: bool) -> BaseObjectData[LobbyParticipant]:
        if lobby_other.data:
            return await general_factory.create_conditional_participant(lobby_other.data, participant_exists, 3)
        return BaseObjectData(-1, True)
