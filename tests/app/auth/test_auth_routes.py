import pytest

from fastapi import Response

from httpx import AsyncClient

from tests.factories.user_factory import UserFactory

from tests.types import InputData, OutputData
from tests.classes.routes import BaseRoutesTest
from tests.factories.general_factory import GeneralFactory

import tests.params.routes.auth as params
from tests.utils.routes_utils import get_protected_routes


@pytest.mark.usefixtures("client_async")
@pytest.mark.parametrize("protected_route", get_protected_routes(params.ROUTES), indirect=True)
class TestAuthRoutes(BaseRoutesTest):
    pass


@pytest.mark.parametrize("data, expected_status, expected_response", params.REGISTER_DATA_STATUS_RESPONSE)
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
@pytest.mark.parametrize("creation_data, data, expected_status, expected_response", params.LOGIN_CREATE_DATA_STATUS_RESPONSE)
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
