from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.models import User

from tests.test_config.factories.token_factory import TokenFactory
from tests.test_config.factories.user_factory import UserFactory


async def create_user_with_tokens(
        user_factory: UserFactory,
        token_factory: TokenFactory,
        role: UserRole = UserRole.USER,
        prefix: str = "testuser",
        password: str = "SecurePassword1!"
) -> tuple[User, str, str]:
    user = await user_factory.create(prefix=prefix, role=role, password=password)
    access_token, refresh_token = await token_factory.create(user)
    return user, access_token, refresh_token
