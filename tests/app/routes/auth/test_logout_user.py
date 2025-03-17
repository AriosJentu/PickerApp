import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.types import InputData
from tests.constants import Roles
from tests.classes.setup import BaseTestSetup


class BaseTestLogoutUser(BaseTestSetup):
    route = "/api/v1/auth/logout"

    async def _send_post_request(self, client_async: AsyncClient, headers: Optional[InputData] = None) -> Response:
        return await client_async.post(self.route, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
@pytest.mark.parametrize("role", Roles.LIST)
class TestLogoutUser(BaseTestLogoutUser):

    @pytest.mark.asyncio
    async def test_logout_success(self, client_async: AsyncClient, base_user_headers: InputData):
        response = await self._send_post_request(client_async, base_user_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


    @pytest.mark.asyncio
    async def test_logout_unauthorized(self, client_async: AsyncClient, role: UserRole):
        response = await self._send_post_request(client_async)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
