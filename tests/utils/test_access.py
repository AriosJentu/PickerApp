from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory

from tests.utils.user_utils import create_user_with_tokens


async def check_access_for_authenticated_users(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        role: UserRole,
        method: str,
        url: str,
        allowed_roles: tuple[UserRole, ...]
):
    _, user_access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {user_access_token}"}

    response: Response = await client_async.request(method, url, headers=headers)

    if role in allowed_roles:
        assert response.status_code != 403, f"Expected not 403, got {response.status_code}"
    else:
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        json_data = response.json()
        assert "Access denied" in str(json_data), f"Permissions error"


async def check_access_for_unauthenticated_users(
        client_async: AsyncClient, 
        method: str, 
        url: str
):
    response: Response = await client_async.request(method, url)
    assert response.status_code == 401, f"Expected 401 for non-authenticated, got {response.status_code}"
    assert "Not authenticated" in str(response.json())
