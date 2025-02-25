from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, asc, desc
from sqlalchemy.orm import selectinload

from app.models.lobby.team import Team
from app.models.lobby.lobby import Lobby
from app.schemas.lobby.team import TeamUpdate


async def db_create_team(db: AsyncSession, team: Team) -> Team:
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


async def db_get_team_by_key_value(db: AsyncSession, key: str, value: str | int) -> Optional[Team]:
    result = await db.execute(
        select(Team)
        .options(
            selectinload(Team.lobby), 
        )
        .filter(getattr(Team, key) == value)
    )
    return result.scalars().first()


async def db_get_team_by_id(db: AsyncSession, team_id: int) -> Optional[Team]:
    return await db_get_team_by_key_value(db, "id", team_id)


async def db_update_team(db: AsyncSession, team: Team, update_data: TeamUpdate) -> Optional[Team]:
    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        return None
    
    await db.execute(update(Team).where(Team.id == team.id).values(**update_dict))
    await db.commit()
    
    await db.refresh(team)
    return team


async def db_delete_team(db: AsyncSession, team: Team) -> bool:
    await db.execute(delete(Team).where(Team.id == team.id))
    await db.commit()
    return True


async def db_get_list_of_teams(
    db: AsyncSession,
    id: Optional[int] = None,
    name: Optional[str] = None,
    lobby: Optional[Lobby] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    only_count: Optional[bool] = False
) -> list[Optional[Team]] | int:
    query = select(Team)

    if id:
        query = query.where(Team.id == id)

    if name:
        query = query.where(Team.name.ilike(f"%{name}%"))
    
    if lobby:
        query.where(Team.lobby_id == lobby.id)

    if only_count:
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        return result.scalar()

    sort_field = getattr(Team, sort_by, None)
    if sort_field:
        query = query.order_by(asc(sort_field) if sort_order == "asc" else desc(sort_field))
    
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()
