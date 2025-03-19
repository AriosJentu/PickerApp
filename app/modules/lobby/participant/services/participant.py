from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session

from app.modules.lobby.lobby.enums import LobbyParticipantRole
from app.modules.lobby.lobby.schemas import LobbyParticipantCreate, LobbyParticipantUpdate
from app.modules.lobby.participant.crud import LobbyParticipantCRUD
from app.modules.lobby.participant.models import LobbyParticipant

from app.shared.service import BaseService


class LobbyParticipantService(BaseService[LobbyParticipant, LobbyParticipantCRUD]):

    def __init__(self, db: AsyncSession = Depends(get_async_session)):
        super().__init__(LobbyParticipant, LobbyParticipantCRUD, db)


    async def get_by_id(self, lobby_id: int, participant_id: int) -> Optional[LobbyParticipant]:
        return await self.crud.get_by_id(lobby_id, participant_id)


    async def get_by_user_id(self, lobby_id: int, user_id: int, is_active: Optional[bool] = None) -> Optional[LobbyParticipant]:
        return await self.crud.get_by_user_id(lobby_id, user_id, is_active)


    async def create(self, participant: LobbyParticipant) -> LobbyParticipant:
        return await self.crud.create(participant)


    async def is_in_lobby(self, lobby_id: int, user_id: int) -> bool:
        participant = await self.get_by_user_id(lobby_id, user_id)
        return participant is not None


    async def add(self, lobby_id: int, user_id: int, team_id: Optional[int] = None) -> LobbyParticipant:
        participant_scheme = LobbyParticipantCreate(
            user_id=user_id,
            lobby_id=lobby_id,
            team_id=team_id,
            role=LobbyParticipantRole.SPECTATOR,
            is_active=True
        )
        new_participant = LobbyParticipant.from_create(participant_scheme)
        return await self.crud.create(new_participant)


    async def leave(self, participant: LobbyParticipant) -> Optional[LobbyParticipant]:
        update_data = LobbyParticipantUpdate(is_active=False)
        return await self.crud.update(participant, update_data)
