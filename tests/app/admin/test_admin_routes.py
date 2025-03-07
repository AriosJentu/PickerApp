import pytest

from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.types import RouteBaseFixture
from tests.constants import Roles
from tests.factories.general_factory import GeneralFactory

import tests.params.routes.admin as params
from tests.params.routes.common import get_role_status_response_for_admin_params
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.routes_utils import get_protected_routes


all_routes = [
    ("DELETE",  "/api/v1/admin/clear-tokens", Roles.ADMIN),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_admin_routes_access(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        protected_route: RouteBaseFixture,
        role: UserRole
):
    await check_access_for_authenticated_users(client_async, general_factory, protected_route, role)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
async def test_admin_routes_require_auth(
        client_async: AsyncClient, 
        protected_route: RouteBaseFixture,
):
    await check_access_for_unauthenticated_users(client_async, protected_route)


@pytest.mark.asyncio
@pytest.mark.parametrize("tokens_response_substr", params.ADMIN_TOKENS_RESPONSE)
@pytest.mark.parametrize("role, expected_status, response_substr", get_role_status_response_for_admin_params())
async def test_clear_inactive_tokens(
        client_async: AsyncClient, 
        general_factory: GeneralFactory,
        response_substr: str,
        tokens_response_substr: str,
        expected_status: int,
        role: UserRole,
):
    
    route = "/api/v1/admin/clear-tokens"
    base_user_data = await general_factory.create_base_user(role)

    response: Response = await client_async.delete(route, headers=base_user_data.headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if expected_status == 200:
        assert tokens_response_substr in str(json_data["detail"]), f"Unexpected response data: {json_data}"
        return 
    
    assert response_substr in str(json_data["detail"]), f"Unexpected response data: {json_data}"
