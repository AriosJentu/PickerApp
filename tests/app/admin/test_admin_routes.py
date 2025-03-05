import pytest

from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.types import BaseUserFixtureCallable, RouteBaseFixture
from tests.constants import Roles
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.routes_utils import get_protected_routes

from tests.utils.common_fixtures import test_base_user_from_role, protected_route


all_routes = [
    ("DELETE",  "/api/v1/admin/clear-tokens", Roles.ADMIN),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_admin_routes_access(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole
):
    await check_access_for_authenticated_users(client_async, protected_route, test_base_user_from_role, role)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
async def test_admin_routes_require_auth(
        client_async: AsyncClient, 
        protected_route: RouteBaseFixture,
):
    await check_access_for_unauthenticated_users(client_async, protected_route)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role, expected_status, response_substr", 
    [
        (UserRole.USER,         403,    "Access denied"),
        (UserRole.MODERATOR,    403,    "Access denied"),
        (UserRole.ADMIN,        200,    "inactive tokens from base")
    ]
)
async def test_clear_inactive_tokens(
        client_async: AsyncClient, 
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole,
        response_substr: str,
        expected_status: int,
):
    
    route = "/api/v1/admin/clear-tokens"
    _, headers = await test_base_user_from_role(role)

    response: Response = await client_async.delete(route, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    assert response_substr in str(json_data["detail"]), f"Unexpected response data: {json_data}"
