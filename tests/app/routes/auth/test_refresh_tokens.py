import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.auth.user.enums import UserRole

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData
from tests.classes.setup import BaseTestSetup


class BaseTestRefreshTokens(BaseTestSetup):
    route = "/api/v1/auth/refresh"

    async def _send_post_request(self, client_async: AsyncClient, headers: Optional[InputData] = None) -> Response:
        return await client_async.post(self.route, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
@pytest.mark.parametrize("role", Roles.LIST)
class TestRefreshTokens(BaseTestRefreshTokens):

    @pytest.mark.asyncio
    async def test_refresh_tokens_success(self, client_async: AsyncClient, base_user_refresh: BaseUserData):
        response = await self._send_post_request(client_async, base_user_refresh.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "access_token" in json_data, "Response should contain access_token"
        assert "refresh_token" in json_data, "Response should contain refresh_token"


    @pytest.mark.asyncio
    async def test_refresh_tokens_using_access_token(self, client_async: AsyncClient, base_user: BaseUserData):
        response = await self._send_post_request(client_async, base_user.headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


    @pytest.mark.asyncio
    async def test_refresh_tokens_missing(self, client_async: AsyncClient, role: UserRole):
        response = await self._send_post_request(client_async)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
