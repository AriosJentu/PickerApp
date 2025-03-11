import pytest

from fastapi import Response

from httpx import AsyncClient

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData
from tests.classes.setup import BaseTestSetup

import tests.params.routes.users as params


class BaseTestClearUserTokens(BaseTestSetup):
    route = "/api/v1/users/tokens"

    async def _send_delete_request(self, client_async, params: InputData, headers: InputData | None = None) -> Response:
        return await client_async.delete(self.route, params=params, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestClearUserTokens(BaseTestClearUserTokens):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_clear_user_tokens_success(self,
            client_async: AsyncClient,
            base_user: BaseUserData,
            base_admin: BaseUserData
    ):
        params = {"get_user_id": base_user.user.id}
        response = await self._send_delete_request(client_async, params, base_admin.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["detail"] == f"Tokens for user with ID {base_user.user.id} has been deactivated", "Deactivation message mismatch"


    @pytest.mark.asyncio
    async def test_clear_user_tokens_missing_parameters(self,
            client_async: AsyncClient,
            base_admin: BaseUserData
    ):
        response = await self._send_delete_request(client_async, {}, base_admin.headers)
        json_data = response.json()
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "No data provided" in json_data["detail"], f"Expected 'No data provided', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("role", Roles.LIST_NON_ADMIN)
    async def test_clear_user_tokens_forbidden(self,
            client_async, 
            base_user: BaseUserData,
    ):
        params = {"get_user_id": base_user.user.id}
        response = await self._send_delete_request(client_async, params, base_user.headers)
        json_data = response.json()

        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "Access denied" in json_data["detail"], f"Expected 'Access denied', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("params", params.USERS_NONEXISTANT_DATA)
    async def test_clear_user_tokens_not_found(self,
            client_async: AsyncClient,
            base_admin: BaseUserData,
            params: InputData
    ):
        response = await self._send_delete_request(client_async, params, base_admin.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "User not found" in json_data["detail"], f"Expected 'User not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    async def test_clear_user_tokens_unauthorized(self, client_async: AsyncClient):
        params = {"get_user_id": 1}
        response = await self._send_delete_request(client_async, params)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
