from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.lobby.lobby.enums import LobbyStatus
from app.modules.lobby.lobby.models import Lobby

from app.shared.crud import BaseCRUD
from app.shared.filters import FilterField


class LobbyCRUD(BaseCRUD[Lobby]):

    default_filters = {
        "id": FilterField(int),
        "name": FilterField(str),
        "host_id": FilterField(int),
        "algorithm_id": FilterField(int),
        "status": FilterField(LobbyStatus),
        "only_active": FilterField(bool, True, ignore=True)
    }


    def __init__(self, db: AsyncSession):
        super().__init__(db, Lobby)


    def custom_filters(self, filters: dict[str, Any]) -> list[Any]:
        conditions = []

        if filters.get("only_active"):
            conditions.append(Lobby.status == LobbyStatus.ACTIVE)

        return conditions
