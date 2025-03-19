import pytest

from fastapi import Response

from httpx import AsyncClient

from tests.utils.types import InputData
from tests.utils.constants import Roles
from tests.utils.dataclasses import BaseUserData
from tests.classes.setup import BaseTestSetup

import tests.params.routes.auth as params


class BaseTestRegisterUser(BaseTestSetup):
    route = "/api/v1/auth/register"

    async def _send_post_request(self, client_async: AsyncClient, json_data: InputData) -> Response:
        return await client_async.post(self.route, json=json_data)


    @pytest.fixture
    async def existing_user(self, base_user: BaseUserData) -> InputData:
        return {"username": base_user.user.username, "email": base_user.user.email}


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestRegisterUser(BaseTestRegisterUser):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_data", params.REGISTER_USER_VALID_DATA)
    async def test_register_success(self, client_async: AsyncClient, user_data: InputData):
        response = await self._send_post_request(client_async, user_data)
        json_data = response.json()

        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        assert "id" in json_data, "Response should contain user ID"
        assert json_data["username"] == user_data["username"], "Username does not match"
        assert json_data["email"] == user_data["email"], "Email does not match"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_data", params.REGISTER_USER_VALID_DATA)
    @pytest.mark.parametrize("duplicate_field, expected_status, error_message", params.REGISTER_USER_DUPLICATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_register_duplicate(self,
            client_async: AsyncClient,
            existing_user: InputData,
            user_data: InputData,
            duplicate_field: str,
            expected_status: int,
            error_message: str
    ):
        new_user_data = user_data.copy()
        new_user_data[duplicate_field] = existing_user[duplicate_field]

        response = await self._send_post_request(client_async, new_user_data)
        json_data = response.json()

        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        assert error_message in json_data["detail"], f"Expected error '{error_message}', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_data, error_message", params.REGISTER_USER_INVALID_DATA)
    async def test_register_invalid_data(self, 
            client_async: AsyncClient,
            user_data: InputData,
            error_message: str
    ):
        response = await self._send_post_request(client_async, user_data)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert error_message in str(json_data["detail"]), f"Expected error '{error_message}', got '{json_data["detail"]}'"
