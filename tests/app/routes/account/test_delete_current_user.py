import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.types import InputData
from tests.constants import Roles
from tests.classes.setup import BaseTestSetup


class BaseTestDeleteUser(BaseTestSetup):
    route = "/api/v1/account/"

    async def _send_delete_request(self, client_async: AsyncClient, headers: Optional[InputData] = None) -> Response:
        return await client_async.delete(self.route, headers=headers or {})
    

@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
@pytest.mark.parametrize("role", Roles.LIST)
class TestDeleteUser(BaseTestDeleteUser):

    @pytest.mark.asyncio
    async def test_delete_current_user_success(self, client_async: AsyncClient, base_user_headers: InputData):
        response = await self._send_delete_request(client_async, base_user_headers)

        assert response.status_code == 204, f"Expected 204, got {response.status_code}"
        assert response.text == "", "Response should be empty on successful delete"


    @pytest.mark.asyncio
    async def test_delete_current_user_unauthorized(self, client_async: AsyncClient, role: UserRole):
        response = await self._send_delete_request(client_async)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
