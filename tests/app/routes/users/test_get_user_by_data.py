import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.auth.user.enums import UserRole

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData
from tests.classes.setup import BaseTestSetup

import tests.params.routes.users as params


class BaseTestGetUser(BaseTestSetup):
    route = "/api/v1/users/"

    async def _send_get_request(self, client_async: AsyncClient, params: InputData, headers: Optional[InputData] = None) -> Response:
        return await client_async.get(self.route, params=params, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
@pytest.mark.parametrize("role", Roles.LIST)
class TestGetUser(BaseTestGetUser):

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, client_async: AsyncClient, base_user: BaseUserData):
        params = {"get_user_id": base_user.user.id}
        response = await self._send_get_request(client_async, params, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == base_user.user.id, "User ID does not match"


    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, client_async: AsyncClient, base_user: BaseUserData):
        params = {"get_username": base_user.user.username}
        response = await self._send_get_request(client_async, params, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["username"] == base_user.user.username, "Username does not match"


    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, client_async: AsyncClient, base_user: BaseUserData):
        params = {"get_email": base_user.user.email}
        response = await self._send_get_request(client_async, params, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["username"] == base_user.user.username, "Username does not match"


    @pytest.mark.asyncio
    async def test_get_user_missing_parameters(self, client_async: AsyncClient, base_user: BaseUserData):
        response = await self._send_get_request(client_async, {}, base_user.headers)
        json_data = response.json()
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "No data provided" in json_data["detail"], f"Expected 'No data provided', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_data", params.USERS_NONEXISTANT_DATA)
    async def test_get_user_not_found(self, client_async: AsyncClient, base_user: BaseUserData, user_data: InputData):
        response = await self._send_get_request(client_async, user_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "User not found" in json_data["detail"], f"Expected 'User not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    async def test_get_user_unauthorized(self, client_async: AsyncClient, role: UserRole):
        params = {"get_user_id": 1}
        response = await self._send_get_request(client_async, params)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
