from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import User, Algorithm, Lobby, LobbyParticipant, Team
from app.enums.user import UserRole

from tests.dataclasses import BaseUserData, BaseObjectData
from tests.types import InputData

from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory
from tests.factories.algorithm_factory import AlgorithmFactory
from tests.factories.lobby_factory import LobbyFactory
from tests.factories.team_factory import TeamFactory
from tests.factories.participant_factory import ParticipantFactory

from tests.utils.user_utils import create_user_with_tokens

class GeneralFactory:

    def __init__(self,
            db_async: AsyncSession,
            user_factory: UserFactory,
            token_factory: TokenFactory,
            algorithm_factory: AlgorithmFactory,
            lobby_factory: LobbyFactory,
            team_factory: TeamFactory,
            participant_factory: ParticipantFactory
    ):
        self.db_async = db_async
        self.user_factory = user_factory
        self.token_factory = token_factory
        self.algorithm_factory = algorithm_factory
        self.lobby_factory = lobby_factory
        self.team_factory = team_factory
        self.participant_factory = participant_factory


    async def create_base_user(self,
            role: UserRole = UserRole.USER,
            is_refresh_token: bool = False,
            prefix: str = "testuser",
            password: str = "SecurePassword1!"
    ) -> BaseUserData:
        user, access_token, refresh_token = await create_user_with_tokens(self.user_factory, self.token_factory, role, prefix, password)
        headers = {"Authorization": f"Bearer {refresh_token if is_refresh_token else access_token}"}
        
        return BaseUserData(user, access_token, refresh_token, headers)
    

    async def create_extra_user(self,
            update_data: InputData,
            is_duplicate_email: bool = False,
            is_duplicate_username: bool = False,
            is_failed: bool = False
    ) -> Optional[User]:
        
        if is_failed:
            return
        
        default_data = {
            "username": "someusername_extra",
            "email":    "somemail_extra@example.com",
            "password": "SecurePassword1!",
            "role":     UserRole.USER
        }

        if is_duplicate_email:
            default_data["email"] = update_data["email"]

        if is_duplicate_username:
            default_data["username"] = update_data["username"]

        return await self.user_factory.create_from_data(default_data)
    

    async def create_conditional_algorithm(self,
        user: User,
        is_algorithm_exists: bool = True,
        i: int = 1
    ) -> BaseObjectData[Algorithm]:
        if not is_algorithm_exists:
            return BaseObjectData(-1, None)
        
        algorithm = await self.algorithm_factory.create(user, i)
        return BaseObjectData(algorithm.id, algorithm)
    

    async def create_conditional_lobby(self,
        user: User,
        is_lobby_exists: bool = True,
        i: int = 1
    ) -> BaseObjectData[Lobby]:
        if not is_lobby_exists:
            return BaseObjectData(-1, None)
        
        algorithm_data = await self.create_conditional_algorithm(user, i)
        lobby = await self.lobby_factory.create(user, algorithm_data.data, i)
        return BaseObjectData(lobby.id, lobby)
    

    async def create_conditional_team(self,
        lobby: Lobby, 
        is_team_exists: bool = True,
        i: int = 1
    ) -> BaseObjectData[Team]:
        if not is_team_exists:
            return BaseObjectData(-1, None)
        
        team = await self.team_factory.create(lobby, i)
        return BaseObjectData(team.id, team)
    
    
    async def create_conditional_participant(self,
        lobby: Lobby,
        is_participant_exists: bool = True,
        i: int = 1
    ) -> BaseObjectData[LobbyParticipant]:
        if not is_participant_exists:
            return BaseObjectData(-1, None)
        
        participant = await self.participant_factory.create(lobby, i)
        return BaseObjectData(participant.id, participant)
    

    async def create_participant_from_user(self,
        user: BaseUserData,
        lobby: Lobby
    ) -> BaseObjectData[LobbyParticipant]:
        participant = await self.participant_factory.create_from_user(user.user, lobby)
        return BaseObjectData(participant.id, participant)
