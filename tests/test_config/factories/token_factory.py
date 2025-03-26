from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.models import User
from app.modules.auth.token.services.token import TokenService


class TokenFactory:

    def __init__(self, db_async: AsyncSession):
        self.service = TokenService(db_async)

    async def create(self, user: User) -> tuple[str, str]:
        access_token = await self.service.create_access_token(user)
        refresh_token = await self.service.create_refresh_token(user)
        return access_token.token, refresh_token.token
