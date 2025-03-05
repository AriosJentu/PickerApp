import pytest

from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.types import BaseUserFixtureCallable, InputData, RouteBaseFixture
from tests.constants import Roles
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.routes_utils import get_protected_routes
from tests.utils.common_fixtures import test_base_user_from_role, protected_route


all_routes = [
    ("GET",     "/api/v1/account/",             Roles.ALL_ROLES),
    ("PUT",     "/api/v1/account/",             Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/account/",             Roles.ALL_ROLES),
    ("GET",     "/api/v1/account/check-token",  Roles.ALL_ROLES),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_account_routes_access(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole
):
    await check_access_for_authenticated_users(client_async, protected_route, test_base_user_from_role, role)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
async def test_account_routes_require_auth(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
):
    await check_access_for_unauthenticated_users(client_async, protected_route)


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_current_user_with_role(
        client_async: AsyncClient, 
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole
):
    
    route = "/api/v1/account/"
    user, headers = await test_base_user_from_role(role)

    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    user_data = response.json()
    assert user_data["username"] == user.username, f"Expected username: {user.username}, got {user_data["username"]}"
    assert user_data["email"] == user.email, f"Expected email: {user.email}, got {user_data["email"]}"
    assert user_data["role"] == str(user.role), f"Expected role: {str(user.role)}, got {user_data["role"]}"


@pytest.mark.asyncio
@pytest.mark.parametrize("update_data", [{"email": "updated_email@example.com"}])
@pytest.mark.parametrize("role", Roles.LIST)
async def test_update_current_user(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        update_data: InputData,
        role: UserRole
):
    
    route = "/api/v1/account/"
    _, headers = await test_base_user_from_role(role)
    
    response: Response = await client_async.put(route, headers=headers, json=update_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert "access_token" in json_data, "Response does not contain access_token"
    assert "refresh_token" in json_data, "Response does not contain refresh_token"

    assert json_data["token_type"] == "bearer", "Unexpected token_type"
    assert json_data["access_token"] != "", "access_token is empty"
    assert json_data["refresh_token"] != "", "refresh_token is empty"

    user_access_token = json_data["access_token"]
    headers = {"Authorization": f"Bearer {user_access_token}"}

    user_info: Response = await client_async.get(route, headers=headers)
    assert user_info.status_code == 200, f"Expected 200, got {response.status_code}"
    
    user_data = user_info.json()
    assert user_data["email"] == update_data["email"]


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_delete_current_user(
        client_async: AsyncClient, 
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole
):
    
    route = "/api/v1/account/"
    _, headers = await test_base_user_from_role(role)

    response: Response = await client_async.delete(route, headers=headers)
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"

    deleted_info: Response = await client_async.delete(route, headers=headers)
    assert deleted_info.status_code == 401, f"Expected 401 for unexistant user, got {deleted_info.status_code}"
    assert "Authorization token is invalid or expired" in str(deleted_info.json())


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_check_token(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole
):
    
    route = "/api/v1/account/check-token"
    user, headers = await test_base_user_from_role(role)

    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["active"] is True, "Expected token state `Active`"
    assert json_data["username"] == user.username, f"Expected username: {user.username}, got {json_data['username']}"
    assert json_data["email"] == user.email, f"Expected email: {user.email}, got {json_data['email']}"
    assert json_data["role"] == user.role, f"Expected role: {user.role}, got {json_data['role']}"
    assert json_data["detail"] == "Token is valid", "Expected detail `Token is valid`"
