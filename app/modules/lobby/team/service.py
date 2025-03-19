from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.lobby.team.crud import TeamCRUD
from app.modules.lobby.team.models import Team
from app.modules.lobby.team.schemas import TeamCreate, TeamUpdate


async def get_team_by_id(db: AsyncSession, team_id: int) -> Optional[Team]:
    crud = TeamCRUD(db)
    return await crud.get_by_id(team_id)


async def create_team(db: AsyncSession, team: TeamCreate) -> Team:
    crud = TeamCRUD(db)
    new_team = Team.from_create(team)
    return await crud.create(new_team)


async def update_team(db: AsyncSession, team: Team, update_data: TeamUpdate) -> Team:
    crud = TeamCRUD(db)
    return await crud.update(team, update_data)


async def delete_team(db: AsyncSession, team: Team) -> bool:
    crud = TeamCRUD(db)
    return await crud.delete(team)


async def get_list_of_teams(
    db: AsyncSession, 
    id: Optional[int] = None,
    lobby_id: Optional[int] = None,
    name: Optional[str] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    only_count: Optional[bool] = False
) -> list[Optional[Team]] | int:
    
    crud = TeamCRUD(db)
    filters = {"id": id, "lobby_id": lobby_id, "name": name}
    return await crud.get_list(filters, sort_by, sort_order, limit, offset, only_count)
