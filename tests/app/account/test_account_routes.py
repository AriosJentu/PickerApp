import pytest

from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.types import InputData, RouteBaseFixture
from tests.constants import Roles
from tests.factories.general_factory import GeneralFactory

import tests.params.routes.account as params
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.routes_utils import get_protected_routes


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
        general_factory: GeneralFactory,
        protected_route: RouteBaseFixture,
        role: UserRole
):
    await check_access_for_authenticated_users(client_async, general_factory, protected_route, role)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
async def test_account_routes_require_auth(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
):
    await check_access_for_unauthenticated_users(client_async, protected_route)


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_current_user(
        client_async: AsyncClient, 
        general_factory: GeneralFactory,
        role: UserRole
):
    
    route = "/api/v1/account/"
    base_user_data = await general_factory.create_base_user(role)

    response: Response = await client_async.get(route, headers=base_user_data.headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    user_data = response.json()
    assert user_data["username"] == base_user_data.user.username, f"Expected username: {base_user_data.user.username}, got {user_data["username"]}"
    assert user_data["email"] == base_user_data.user.email, f"Expected email: {base_user_data.user.email}, got {user_data["email"]}"
    assert user_data["role"] == str(base_user_data.user.role), f"Expected role: {str(base_user_data.user.role)}, got {user_data["role"]}"


@pytest.mark.asyncio
@pytest.mark.parametrize("update_data, expected_status, error_substr", params.UPDATE_USER_DATA_STATUS_ERROR)
@pytest.mark.parametrize("duplicate_email, expected_status_email, error_email_substr", params.UPDATE_USER_DUPLICATE_EMAIL_EXPECT_ERROR)
@pytest.mark.parametrize("duplicate_username, expected_status_username, error_username_substr", params.UPDATE_USER_DUPLICATE_USERNAME_EXPECT_ERROR)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_update_current_user(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        update_data: InputData,
        role: UserRole,
        duplicate_email: bool,
        duplicate_username: bool,
        expected_status: int,
        expected_status_email: int,
        expected_status_username: int,
        error_substr: str,
        error_email_substr: str,
        error_username_substr: str
):
    route = "/api/v1/account/"
    base_user_data = await general_factory.create_base_user(role)

    duplicate_email = duplicate_email and "email" in update_data
    duplicate_username = duplicate_username and "username" in update_data
    await general_factory.create_extra_user(update_data, duplicate_email, duplicate_username, expected_status == 422)

    response: Response = await client_async.put(route, headers=base_user_data.headers, json=update_data)
    json_data = response.json()

    if expected_status != 200:
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        message = json_data["detail"][0]["msg"]
        assert error_substr in str(message), f"Expected error '{error_substr}', got {message}"
        return

    if duplicate_email:
        assert response.status_code == expected_status_email, f"Expected {expected_status_email}, got {response.status_code}"
        assert error_email_substr in str(json_data["detail"]), f"Expected error '{error_email_substr}', got {json_data['detail']}"
        return

    if duplicate_username:
        assert response.status_code == expected_status_username, f"Expected {expected_status_username}, got {response.status_code}"
        assert error_username_substr in str(json_data["detail"]), f"Expected error '{error_username_substr}', got {json_data['detail']}"
        return

    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    assert "access_token" in json_data, "Response does not contain access_token"
    assert "refresh_token" in json_data, "Response does not contain refresh_token"

    user_access_token = json_data["access_token"]
    headers = {"Authorization": f"Bearer {user_access_token}"}

    user_info: Response = await client_async.get(route, headers=headers)
    assert user_info.status_code == 200, f"Expected 200, got {user_info.status_code}"

    user_data = user_info.json()
    if "email" in update_data:
        assert user_data["email"] == update_data["email"], "Email was not updated"
    if "username" in update_data:
        assert user_data["username"] == update_data["username"], "Username was not updated"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_delete_current_user(
        client_async: AsyncClient, 
        general_factory: GeneralFactory,
        role: UserRole
):
    
    route = "/api/v1/account/"
    base_user_data = await general_factory.create_base_user(role)

    response: Response = await client_async.delete(route, headers=base_user_data.headers)
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"

    deleted_info: Response = await client_async.delete(route, headers=base_user_data.headers)
    assert deleted_info.status_code == 401, f"Expected 401 for deleted user, got {deleted_info.status_code}"
    assert "Authorization token is invalid or expired" in str(deleted_info.json())


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_check_token(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        role: UserRole
):
    
    route = "/api/v1/account/check-token"
    base_user_data = await general_factory.create_base_user(role)

    response: Response = await client_async.get(route, headers=base_user_data.headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["active"] is True, "Expected token state `Active`"
    assert json_data["username"] == base_user_data.user.username, f"Expected username: {base_user_data.user.username}, got {json_data['username']}"
    assert json_data["email"] == base_user_data.user.email, f"Expected email: {base_user_data.user.email}, got {json_data['email']}"
    assert json_data["role"] == base_user_data.user.role, f"Expected role: {base_user_data.user.role}, got {json_data['role']}"
    assert json_data["detail"] == "Token is valid", "Expected detail `Token is valid`"
