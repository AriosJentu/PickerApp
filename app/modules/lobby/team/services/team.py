from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session

from app.modules.lobby.team.crud import TeamCRUD
from app.modules.lobby.team.models import Team

from app.shared.service import BaseService


class TeamService(BaseService[Team, TeamCRUD]):

    def __init__(self, db: AsyncSession = Depends(get_async_session)):
        super().__init__(Team, TeamCRUD, db)
