from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, asc, desc

from app.db.base import User
from app.enums.user import UserRole
from app.schemas.auth.user import UserCreate, UserUpdateSecure, UserUpdate


type UserExistType = tuple[bool, bool]
type UserTupleType = tuple[User, User]


async def db_create_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def db_get_user_by_key_value(db: AsyncSession, key: str, value: str | int) -> Optional[User]:
    result = await db.execute(select(User).filter(getattr(User, key) == value))
    return result.scalars().first()


async def db_get_user_by_keys_values(db: AsyncSession, keys: tuple[str], values: tuple[str]) -> Optional[User]:
    query = select(User)
    for key, value in zip(keys, values):
        query = query.filter(getattr(User, key) == value)

    result = await db.execute(query)
    return result.scalars().first()


async def db_get_users_by_username_email(db: AsyncSession, user: UserCreate | UserUpdateSecure | UserUpdate) -> UserTupleType:
    user_by_username = await db_get_user_by_key_value(db, "username", user.username)
    user_by_email = await db_get_user_by_key_value(db, "email", user.email)
    return user_by_username, user_by_email


async def db_is_user_exist(db: AsyncSession, user: UserCreate | UserUpdateSecure | UserUpdate) -> UserExistType:
    user_by_username, user_by_email = await db_get_users_by_username_email(db, user)
    return user_by_username is not None, user_by_email is not None


async def db_update_user(db: AsyncSession, user: User, update_data: UserUpdateSecure | UserUpdate) -> Optional[User]:
    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        return None
    
    await db.execute(update(User).where(User.id == user.id).values(**update_dict))
    await db.commit()
    
    await db.refresh(user)
    return user


async def db_delete_user(db: AsyncSession, user: User) -> bool:
    await db.execute(delete(User).where(User.id == user.id))
    await db.commit()
    return True


async def db_get_list_of_users(
    db: AsyncSession,
    id: Optional[int] = None,
    role: Optional[UserRole] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    external_id: Optional[str] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    only_count: Optional[bool] = False
) -> list[Optional[User]] | int:
    
    query = select(User)

    if id:
        query = query.where(User.id == id)

    if external_id:
        query = query.where(User.external_id.ilike(f"%{external_id}%"))

    if role:
        query = query.where(User.role == role)

    if username:
        query = query.where(User.username.ilike(f"%{username}%"))

    if email:
        query = query.where(User.email.ilike(f"%{email}%"))

    if only_count:
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        return result.scalar()

    sort_field = getattr(User, sort_by, None)
    if sort_field:
        query = query.order_by(asc(sort_field) if sort_order == "asc" else desc(sort_field))

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()
