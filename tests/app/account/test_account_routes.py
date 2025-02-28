import pytest

from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory

from tests.utils.user_utils import create_user_with_tokens, Roles
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.routes_utils import get_protected_routes


all_routes = [
    ("GET",     "/api/v1/account/",             Roles.ALL_ROLES),
    ("PUT",     "/api/v1/account/",             Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/account/",             Roles.ALL_ROLES),
    ("GET",     "/api/v1/account/check-token",  Roles.ALL_ROLES),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("method, url, allowed_roles", get_protected_routes(all_routes))
async def test_account_routes_access(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        role: UserRole,
        method: str,
        url: str,
        allowed_roles: tuple[UserRole, ...]
):
    await check_access_for_authenticated_users(client_async, user_factory, token_factory, role, method, url, allowed_roles)


@pytest.mark.asyncio
@pytest.mark.parametrize("method, url, allowed_roles", get_protected_routes(all_routes))
async def test_account_routes_require_auth(
        client_async: AsyncClient, 
        method: str, 
        url: str, 
        allowed_roles: tuple[UserRole, ...]
):
    await check_access_for_unauthenticated_users(client_async, method, url)


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_current_user_with_role(
        client_async: AsyncClient, 
        user_factory: UserFactory,
        token_factory: TokenFactory,
        role: UserRole
):
    
    route = "/api/v1/account/"
    user, user_access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)

    headers = {"Authorization": f"Bearer {user_access_token}"}
    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    user_data = response.json()
    assert user_data["username"] == user.username, f"Expected username: {user.username}, got {user_data["username"]}"
    assert user_data["email"] == user.email, f"Expected email: {user.email}, got {user_data["email"]}"
    assert user_data["role"] == str(role), f"Expected role: {str(role)}, got {user_data["role"]}"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_update_current_user(
        client_async: AsyncClient, 
        user_factory: UserFactory,
        token_factory: TokenFactory,
        role: UserRole
):
    
    route = "/api/v1/account/"
    _, user_access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    
    headers = {"Authorization": f"Bearer {user_access_token}"}
    update_data = {"email": "updated_email@example.com"}

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
        user_factory: UserFactory,
        token_factory: TokenFactory,
        role: UserRole
):
    
    route = "/api/v1/account/"
    _, user_access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)

    headers = {"Authorization": f"Bearer {user_access_token}"}
    response: Response = await client_async.delete(route, headers=headers)
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"


    deleted_info: Response = await client_async.delete(route, headers=headers)
    assert deleted_info.status_code == 401, f"Expected 401 for unexistant user, got {deleted_info.status_code}"
    assert "Authorization token is invalid or expired" in str(deleted_info.json())


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_check_token(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        role: UserRole
):
    
    route = "/api/v1/account/check-token"
    user, user_access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)

    headers = {"Authorization": f"Bearer {user_access_token}"}
    response: Response = await client_async.get(route, headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["active"] is True, "Expected token state `Active`"
    assert json_data["username"] == user.username, f"Expected username: {user.username}, got {json_data['username']}"
    assert json_data["email"] == user.email, f"Expected email: {user.email}, got {json_data['email']}"
    assert json_data["detail"] == "Token is valid", "Expected detail `Token is valid`"
