import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.db.base import Lobby

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup


class BaseTestGetLobby(BaseTestSetup):
    route = "/api/v1/lobby/{lobby_id}"

    async def _send_get_request(self, client_async: AsyncClient, lobby: BaseObjectData[Lobby], headers: Optional[InputData] = None) -> Response:
        return await client_async.get(self.route.format(lobby_id=lobby.id), headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestGetLobby(BaseTestGetLobby):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_get_lobby_success(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            base_user: BaseUserData
    ):
        response = await self._send_get_request(client_async, lobby, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == lobby.id, "Lobby ID does not match"
        assert json_data["name"] == lobby.data.name, "Lobby name does not match"
        assert json_data["algorithm"]["id"] == lobby.data.algorithm_id, "Algorithm ID does not match"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_get_lobby_not_found(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            base_user: BaseUserData
    ):
        response = await self._send_get_request(client_async, lobby, base_user.headers)
        json_data = response.json()
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Lobby not found" in json_data["detail"], f"Expected error message 'Lobby not found', got: '{json_data["detail"]}'"
    

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_get_lobby_unauthorized(self, client_async: AsyncClient, lobby: BaseObjectData[Lobby]):
        response = await self._send_get_request(client_async, lobby)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
