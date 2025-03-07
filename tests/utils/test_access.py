from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.types import RouteBaseFixture
from tests.factories.general_factory import GeneralFactory


async def check_access_for_authenticated_users(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        protected_route: RouteBaseFixture,
        role: UserRole
):
    method, url, allowed_roles = protected_route
    base_user_data = await general_factory.create_base_user(role)
    response: Response = await client_async.request(method, url, headers=base_user_data.headers)

    if base_user_data.user.role in allowed_roles:
        assert response.status_code != 403, f"Expected not 403, got {response.status_code}"
    else:
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        json_data = response.json()
        assert "Access denied" in str(json_data), f"Permissions error"


async def check_access_for_unauthenticated_users(
        client_async: AsyncClient, 
        protected_route: RouteBaseFixture,
):
    method, url, _ = protected_route
    response: Response = await client_async.request(method, url)
    assert response.status_code == 401, f"Expected 401 for non-authenticated, got {response.status_code}"
    assert "Not authenticated" in str(response.json())
