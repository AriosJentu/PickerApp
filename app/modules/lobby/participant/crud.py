from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.lobby.lobby.enums import LobbyParticipantRole
from app.modules.lobby.lobby.models import Lobby
from app.modules.lobby.participant.models import LobbyParticipant

from app.shared.crud import BaseCRUD
from app.shared.filters import FilterField


class LobbyParticipantCRUD(BaseCRUD[LobbyParticipant]):

    default_filters = {
        "id": FilterField(int),
        "user_id": FilterField(int),
        "team_id": FilterField(int),
        "lobby": FilterField(Lobby, operator=FilterField.empty), # TODO: Try to understand, why it's not effective, and `lobby` will still be checked in global method `get_list`, and will probaly fail
        "role": FilterField(LobbyParticipantRole),
        "is_active": FilterField(bool),
        "all_db_participants": FilterField(bool, False)
    }


    def __init__(self, db: AsyncSession):
        super().__init__(db, LobbyParticipant)


    async def get_by_key_value(self, lobby: Lobby, key: str, value: Any) -> Optional[LobbyParticipant]:
        result = await self.db.execute(
            select(self.model)
            .filter(
                getattr(self.model, key) == value,
                self.model.lobby_id == lobby.id
            )
        )

        return result.scalars().first()


    async def get_by_id(self, lobby: Lobby, value: int) -> Optional[LobbyParticipant]:
        return await self.get_by_key_value(lobby, "id", value)


    async def get_by_user_id(self, lobby: Lobby, user_id: int, is_active: Optional[bool] = None) -> Optional[LobbyParticipant]:
        query = select(self.model).filter(
            self.model.user_id == user_id,
            self.model.lobby_id == lobby.id
        )

        if is_active is not None:
            query = query.filter(self.model.is_active == is_active)

        result = await self.db.execute(query)
        return result.scalars().first()


    def custom_filters(self, filters: dict[str, Any]) -> list[Any]:
        conditions = []
        if filters.get("all_db_participants") is False and "lobby" in filters:
            conditions.append(LobbyParticipant.lobby_id == filters["lobby"].id)
        return conditions
