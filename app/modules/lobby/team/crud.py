from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.lobby.team.models import Team

from app.shared.crud import BaseCRUD
from app.shared.filters import FilterField


class TeamCRUD(BaseCRUD[Team]):

    default_filters = {
        "id": FilterField(int),
        "name": FilterField(str),
        "lobby_id": FilterField(int)
    }


    def __init__(self, db: AsyncSession):
        super().__init__(db, Team)
