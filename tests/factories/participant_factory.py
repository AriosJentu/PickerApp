from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.models import User
from app.modules.lobby.lobby.models import Lobby
from app.modules.lobby.participant.models import LobbyParticipant
from app.modules.lobby.participant.crud_old import db_create_lobby_participant

from tests.factories.user_factory import UserFactory

class ParticipantFactory:

    def __init__(self, db_async: AsyncSession, user_factory: UserFactory):
        self.db_async = db_async
        self.user_factory = user_factory
    
    async def create_from_user(self, user: User, lobby: Lobby) -> LobbyParticipant:
        data = {
            "user_id": user.id,
            "lobby_id": lobby.id
        }
        participant = LobbyParticipant(**data)
        return await db_create_lobby_participant(self.db_async, participant)

    async def create(self, lobby: Lobby, i: int = 1) -> LobbyParticipant:
        user = await self.user_factory.create(suffix=f"participant{i}")
        return await self.create_from_user(user, lobby)
