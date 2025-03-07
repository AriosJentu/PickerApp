from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import User, Algorithm, Lobby, Team
from app.enums.user import UserRole

from tests.dataclasses import TestBaseUserData, TestObjectData
from tests.types import InputData
from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory
from tests.factories.algorithm_factory import AlgorithmFactory
from tests.factories.lobby_factory import LobbyFactory
from tests.factories.team_factory import TeamFactory

from tests.utils.user_utils import create_user_with_tokens

class GeneralFactory:

    def __init__(self, 
            db_async: AsyncSession,
            user_factory: UserFactory,
            token_factory: TokenFactory,
            algorithm_factory: AlgorithmFactory,
            lobby_factory: LobbyFactory,
            team_factory: TeamFactory,
    ):
        self.db_async = db_async
        self.user_factory = user_factory
        self.token_factory = token_factory
        self.algorithm_factory = algorithm_factory
        self.lobby_factory = lobby_factory
        self.team_factory = team_factory


    async def create_base_user(self, 
            role: UserRole = UserRole.USER,
            is_refresh_token: bool = False,
            prefix: str = "testuser"
    ) -> TestBaseUserData:
        user, access_token, refresh_token = await create_user_with_tokens(self.user_factory, self.token_factory, role, prefix)
        headers = {"Authorization": f"Bearer {refresh_token if is_refresh_token else access_token}"}
        
        return TestBaseUserData(user, access_token, refresh_token, headers)


    async def create_base_users_creator(self,
        role: UserRole = UserRole.USER
    ) -> tuple[TestBaseUserData, ...]:
        user = await self.create_base_user(role)
        creator = await self.create_base_user(prefix="creator_user")
        return user, creator
    

    async def create_base_users_creator_aditional(self,
        role: UserRole = UserRole.USER
    ) -> tuple[TestBaseUserData, ...]:
        user = await self.create_base_user(role)
        creator = await self.create_base_user(prefix="creator_user")
        user_to_add = await self.create_base_user(prefix="user_to_add")
        return user, creator, user_to_add
    

    async def create_extra_user(self,
            update_data: InputData,
            is_duplicate_email: bool = False,
            is_duplicate_username: bool = False,
            is_failed: bool = False
    ) -> User | None:
        
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
        is_algorithm_exists: bool = True
    ) -> TestObjectData[Algorithm]:
        if not is_algorithm_exists:
            return TestObjectData(-1, None)
        
        algorithm = await self.algorithm_factory.create(user)
        return TestObjectData(algorithm.id, algorithm)
    

    async def create_conditional_lobby(self,
        user: User,
        is_lobby_exists: bool = True
    ) -> TestObjectData[Lobby]:
        if not is_lobby_exists:
            return TestObjectData(-1, None)
        
        algorithm_data = await self.create_conditional_algorithm(user)
        lobby = await self.lobby_factory.create(user, algorithm_data.data)
        return TestObjectData(lobby.id, lobby)
    

    async def create_conditional_team(self,
        lobby: Lobby, 
        is_team_exists: bool = True
    ) -> TestObjectData[Team]:
        if not is_team_exists:
            return TestObjectData(-1, None)
        
        team = await self.team_factory.create(lobby)
        return TestObjectData(team.id, team)
