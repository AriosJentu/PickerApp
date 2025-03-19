from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import ColumnElement

from app.modules.lobby.team.models import Team
from app.modules.lobby.lobby.models import Lobby
from app.modules.lobby.team.schemas import TeamUpdate

from app.shared.crud import BaseCRUD
from app.shared.filters import FilterField


def lobby_filter(column: ColumnElement, value: Lobby) -> ColumnElement:
    return column.lobby_id == value.id


class TeamCRUD(BaseCRUD[Lobby]):

    default_filters = {
        "id": FilterField(int),
        "name": FilterField(str),
        "lobby": FilterField(Lobby, operator=lobby_filter) # TODO: Try to understand, why this function is not suppose to do what you expect from it, and how to improve it, maybe add `custom` field to ignore this in processign, but try use function `custom_filters`
    }


    def __init__(self, db: AsyncSession):
        super().__init__(db, Lobby)
