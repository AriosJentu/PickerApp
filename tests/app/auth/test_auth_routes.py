import pytest

from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.factories.user_factory import UserFactory

from tests.types import InputData, OutputData, RouteBaseFixture
from tests.constants import Roles
from tests.factories.general_factory import GeneralFactory

from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.routes_utils import get_protected_routes


all_routes = [
    ("POST", "/api/v1/auth/register",   None),
    ("POST", "/api/v1/auth/login",      None),
    ("POST", "/api/v1/auth/logout",     Roles.ALL_ROLES),
    ("POST", "/api/v1/auth/refresh",    Roles.ALL_ROLES),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_auth_routes_access(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        protected_route: RouteBaseFixture,
        role: UserRole
):
    await check_access_for_authenticated_users(client_async, general_factory, protected_route, role)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
async def test_auth_routes_require_auth(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
):
    await check_access_for_unauthenticated_users(client_async, protected_route)


@pytest.mark.parametrize(
    "data, expected_status, expected_response",
    [
        (
            {"username": "defaultuser",     "email": "defaultuser@example.com",     "password": "SecurePassword1!"},
            201,
            {"username": "defaultuser",     "email": "defaultuser@example.com",     "role": "user"},
        ),
        (
            {"username": "a",               "email": "defaultuser@example.com",     "password": "SecurePassword1!"},
            422,
            {"detail": "Username must be at least 3 characters long"},
        ),
        (
            {"username": "defaultuser",     "email": "invalidemail",                "password": "SecurePassword1!"},
            422,
            {"detail": "An email address must have an @-sign"},
        ),
        (
            {"username": "defaultuser",     "email": "defaultuser@example.com",     "password": "123"},
            422,
            {"detail": "Password must be at least 8 characters long"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_register_user(
        client_async: AsyncClient, 
        data: InputData, 
        expected_status: int, 
        expected_response: OutputData
):

    route = "/api/v1/auth/register"
    response: Response = await client_async.post(route, json=data)

    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    json_data = response.json()

    if expected_status == 201:
        assert json_data["username"] == expected_response["username"]
        assert json_data["email"] == expected_response["email"]
        assert json_data["role"] == expected_response["role"]
    else:
        assert expected_response["detail"] in str(json_data)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "creation_data, data, expected_status, expected_response",
    [
        (
            {"username": "testuser", "email": "test@example.com", "password": "SecurePassword1!", "role": UserRole.USER},
            {"username": "testuser", "password": "SecurePassword1!"},
            200,
            {"token_type": "bearer"},
        ),
        (
            {"username": "testuser", "email": "test@example.com", "password": "SecurePassword1!", "role": UserRole.USER},
            {"username": "testuser", "password": "WrongPassword"},
            401,
            {"detail": "Incorrect username or password"},
        ),
        (
            {"username": "nonexistent", "email": "nonexistent@example.com", "password": "SomePassword", "role": UserRole.USER},
            {"username": "nonexistent", "password": "SomePassword"},
            401,
            {"detail": "Incorrect username or password"},
        ),
    ]
)
async def test_login_user(
        client_async: AsyncClient,
        user_factory: UserFactory,
        creation_data: InputData,
        data: InputData,
        expected_status: int,
        expected_response: OutputData,
):

    route = "/api/v1/auth/login"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    if expected_status == 200:
        await user_factory.create_from_data(creation_data)

    response: Response = await client_async.post(route, data=data, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if expected_status == 200:
        assert "access_token" in json_data
        assert json_data["token_type"] == expected_response["token_type"]
    else:
        assert expected_response["detail"] in str(json_data)


@pytest.mark.asyncio
async def test_logout_user(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
):
    
    route = "/api/v1/auth/logout"
    base_user_data = await general_factory.create_base_user()
    
    response: Response = await client_async.post(route, headers=base_user_data.headers)
    assert response.status_code == 200, f"Expected 200 for Logout, got {response.status_code}"
    assert "Successfully logout" in response.json().get("detail", "")

    response: Response = await client_async.post(route, headers=base_user_data.headers)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    assert "Authorization token is invalid or expired" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_successful_refresh(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
):
    
    route = "/api/v1/auth/refresh"
    check_route = "/api/v1/account/check-token"
    base_user_data = await general_factory.create_base_user(is_refresh_token=True)

    response: Response = await client_async.post(route, headers=base_user_data.headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert "access_token" in json_data and "refresh_token" in json_data, f"Missing tokens: {json_data}"

    new_access_token = json_data["access_token"]
    assert new_access_token != base_user_data.access_token, "New access_token should be different"
    headers = {"Authorization": f"Bearer {new_access_token}"}

    response: Response = await client_async.get(check_route, headers=headers)
    assert response.status_code == 200, f"Expected 200 for new access token, got {response.status_code}"


@pytest.mark.asyncio
async def test_refresh_with_access_token_incorrect(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
):
    
    route = "/api/v1/auth/refresh"
    base_user_data = await general_factory.create_base_user()

    response: Response = await client_async.post(route, headers=base_user_data.headers)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    assert "Invalid authorization token type" in response.json().get("detail", "")
