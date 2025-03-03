from app.db.base import User
from app.enums.user import UserRole

from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory


async def create_user_with_tokens(
        user_factory: UserFactory,
        token_factory: TokenFactory,
        role: UserRole = UserRole.USER,
        prefix: str = "testuser"
) -> tuple[User, str, str]:
    user = await user_factory.create(prefix=prefix, role=role)
    access_token, refresh_token = await token_factory.create(user)
    return user, access_token, refresh_token
