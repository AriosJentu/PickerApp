
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.modules.auth.user.models import User
from app.modules.auth.token.models import Token

from app.core.base.crud import BaseCRUD


class TokenCRUD(BaseCRUD[Token]):

    def __init__(self, db: AsyncSession):
        super().__init__(db, Token)


    async def is_token_exist(self, token_str: str) -> bool:
        
        result = await self.db.execute(
            select(Token)
            .filter(
                Token.token == token_str,
                Token.is_active == True
            )
        )
        return result.scalars().first() is not None


    async def get_users_last_token(self, user: User, token_type: str = "access") -> Optional[Token]:

        result = await self.db.execute(
            select(Token)
            .filter(
                Token.user_id == user.id,
                Token.token_type == token_type,
                Token.is_active == True
            )
            .order_by(Token.expires_at.desc())
        )
        return result.scalars().first()


    async def deactivate_tokens(self, user: User, token_type: str = "all"):
        condition = True if token_type == "all" else (Token.token_type == token_type)
        
        await self.db.execute(
            update(Token)
            .where(
                Token.user_id == user.id,
                Token.is_active == True,
                condition
            )
            .values(is_active=False)
        )

        await self.db.commit()


    async def drop_inactive_tokens(self, user: User) -> int:
        
        result = await self.db.execute(
            delete(Token)
            .where(
                Token.user_id == user.id,
                Token.is_active == False
            )
        )

        await self.db.commit()
        return result.rowcount


    async def drop_all_inactive_tokens(self) -> int:
        
        result = await self.db.execute(
            delete(Token)
            .where(Token.is_active == False)
        )
        
        await self.db.commit()
        return result.rowcount
