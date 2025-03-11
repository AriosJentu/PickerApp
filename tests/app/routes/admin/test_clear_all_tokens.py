import pytest

from fastapi import Response

from httpx import AsyncClient

from tests.types import InputData
from tests.constants import Roles
from tests.classes.setup import BaseTestSetup


class BaseTestClearTokens(BaseTestSetup):
    route = "/api/v1/admin/clear-tokens"

    async def _send_delete_request(self, client_async: AsyncClient, headers: InputData | None = None) -> Response:
        return await client_async.delete(self.route, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestClearTokens(BaseTestClearTokens):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("role", Roles.LIST_ADMIN)
    async def test_clear_tokens_success(self, client_async: AsyncClient, base_user_headers: InputData):
        response = await self._send_delete_request(client_async, base_user_headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["detail"] == "Removed 0 inactive tokens from base", f"Unexpected response: '{json_data}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("role", Roles.LIST_NON_ADMIN)
    async def test_clear_tokens_forbidden(self, client_async: AsyncClient, base_user_headers: InputData):
        response = await self._send_delete_request(client_async, base_user_headers)
        json_data = response.json()

        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "Access denied" in json_data["detail"], f"Expected 'Access denied', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    async def test_clear_tokens_unauthorized(self, client_async: AsyncClient):
        response = await self._send_delete_request(client_async)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

