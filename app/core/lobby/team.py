from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Lobby, Team
from app.schemas.lobby.team import TeamUpdate

from app.crud.lobby.team import (
    db_get_team_by_id,
    db_create_team,
    db_update_team,
    db_delete_team,
    db_get_list_of_teams
)


async def get_team_by_id(db: AsyncSession, team_id: int) -> Optional[Team]:
    return await db_get_team_by_id(db, team_id)


async def create_team(db: AsyncSession, team: Team) -> Team:
    return await db_create_team(db, team)


async def update_team(db: AsyncSession, team: Team, update_data: TeamUpdate) -> Team:
    return await db_update_team(db, team, update_data)


async def delete_team(db: AsyncSession, team: Team):
    return await db_delete_team(db, team)


async def get_list_of_teams(
    db: AsyncSession, 
    id: Optional[int] = None,
    name: Optional[str] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    lobby: Optional[Lobby] = None
) -> list[Team]:
    return await db_get_list_of_teams(db, id, name, sort_by, sort_order, limit, offset, lobby)
