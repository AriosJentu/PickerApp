import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from tests.test_config.classes.setup import BaseTestSetup
from tests.test_config.utils.constants import Roles
from tests.test_config.utils.dataclasses import BaseUserData
from tests.test_config.utils.types import InputData

import tests.test_config.params.routes.users as params


class BaseTestUpdateUser(BaseTestSetup):
    route = "/api/v1/users/"

    async def _send_put_request(self, client_async: AsyncClient, params: InputData, json_data: InputData, headers: Optional[InputData] = None) -> Response:
        return await client_async.put(self.route, params=params, json=json_data, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestUpdateUser(BaseTestUpdateUser):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_data", params.USERS_UPDATE_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_update_user_success(self,
            client_async: AsyncClient,
            base_user: BaseUserData,
            base_admin: BaseUserData,
            update_data: InputData
    ):
        params = {"get_user_id": base_user.user.id}
        response = await self._send_put_request(client_async, params, update_data, base_admin.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        self.assert_update_data(json_data, update_data)


    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_data", params.USERS_UPDATE_VALID_DATA)
    async def test_update_user_missing_parameters(self,
            client_async: AsyncClient,
            base_admin: BaseUserData,
            update_data: InputData,
    ):
        response = await self._send_put_request(client_async, {}, update_data, base_admin.headers)
        json_data = response.json()

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "No data provided" in json_data["detail"], f"Expected 'No data provided', got '{json_data["detail"]}'"
    

    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_data, expected_error", params.USERS_UPDATE_INVALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_update_user_validation_error(self,
            client_async: AsyncClient,
            base_user: BaseUserData,
            base_admin: BaseUserData,
            update_data: InputData,
            expected_error: str,
    ):
        params = {"get_user_id": base_user.user.id}
        response = await self._send_put_request(client_async, params, update_data, base_admin.headers)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert expected_error.lower() in str(json_data).lower(), f"Expected '{expected_error}' in validation errors, got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_data", params.USERS_UPDATE_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST_NON_ADMIN)
    async def test_update_user_forbidden(self,
            client_async: AsyncClient,
            base_user: BaseUserData,
            update_data: InputData
    ):
        params = {"get_user_id": base_user.user.id}
        response = await self._send_put_request(client_async, params, update_data, base_user.headers)
        json_data = response.json()
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "Access denied" in json_data["detail"], f"Expected 'Access denied', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("params", params.USERS_NONEXISTANT_DATA)
    async def test_update_user_not_found(self,
            client_async: AsyncClient,
            base_admin: BaseUserData,
            params: InputData
    ):
        update_data = {"username": "new_user"}
        response = await self._send_put_request(client_async, params, update_data, base_admin.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "User not found" in json_data["detail"], f"Expected 'User not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_data", params.USERS_UPDATE_VALID_DATA)
    async def test_update_user_unauthorized(self, client_async: AsyncClient, update_data: InputData):
        params = {"get_user_id": 1}
        response = await self._send_put_request(client_async, params, update_data)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
