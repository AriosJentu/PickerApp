from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.types import RouteBaseFixture, BaseUserFixtureCallable


async def check_access_for_authenticated_users(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole
):
    method, url, allowed_roles = protected_route
    user, headers = await test_base_user_from_role(role)
    response: Response = await client_async.request(method, url, headers=headers)

    if user.role in allowed_roles:
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
