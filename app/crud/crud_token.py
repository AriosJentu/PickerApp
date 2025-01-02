from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.models.user import User
from app.models.token import Token


async def db_create_token(db: AsyncSession, token: Token) -> Token:
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token


async def db_is_token_exist(db: AsyncSession, token_str: str) -> bool:
    tokens = await db.execute(select(Token).filter(Token.token == token_str, Token.is_active == True))
    
    token_in_db = tokens.scalars().first()
    return token_in_db is not None


async def db_get_users_last_token(db: AsyncSession, user: User, token_type: str = "active") -> Token:
    tokens = await db.execute(select(Token).filter(Token.user_id == user.id, Token.token_type == token_type, Token.is_active == True).order_by(Token.expires_at.desc()))
    return tokens.scalars().first()


async def db_deactivate_tokens(db: AsyncSession, user: User, token_type: str = "all"):
    condition = True
    if token_type != "all":
        condition = (Token.token_type == token_type)
        
    await db.execute(update(Token).where(Token.user_id == user.id, Token.is_active == True, condition).values(is_active=False))
    await db.commit()


async def db_drop_inactive_tokens(db: AsyncSession, user: User) -> int:
    result = await db.execute(delete(Token).where(Token.user_id == user.id, Token.is_active == False))
    await db.commit()
    return result.rowcount


async def db_drop_all_inactive_tokens(db: AsyncSession) -> int:
    result = await db.execute(delete(Token).where(Token.is_active == False))
    await db.commit()
    return result.rowcount
