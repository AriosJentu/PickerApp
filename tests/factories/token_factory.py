from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.models import User
from app.modules.auth.user.service_old import create_user_tokens


class TokenFactory:

    def __init__(self, db_async: AsyncSession):
        self.db_async = db_async

    async def create(self, user: User) -> tuple[str, str]:
        access_token, refresh_token = await create_user_tokens(self.db_async, user)
        return access_token.token, refresh_token.token
