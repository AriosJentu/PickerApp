import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.auth.user.enums import UserRole

from tests.test_config.classes.setup import BaseTestSetup
from tests.test_config.utils.constants import Roles
from tests.test_config.utils.types import InputData


class BaseTestGetUser(BaseTestSetup):
    route = "/api/v1/account/"

    async def _send_get_request(self, client_async: AsyncClient, headers: Optional[InputData] = None) -> Response:
        return await client_async.get(self.route, headers=headers or {})
    

@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
@pytest.mark.parametrize("role", Roles.LIST)
class TestGetUser(BaseTestGetUser):

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, client_async: AsyncClient, base_user_headers: InputData):
        response = await self._send_get_request(client_async, base_user_headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "id" in json_data, "Response does not contain user ID"
        assert "email" in json_data, "Response does not contain email"
        assert "username" in json_data, "Response does not contain username"


    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client_async: AsyncClient, role: UserRole):
        response = await self._send_get_request(client_async)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
