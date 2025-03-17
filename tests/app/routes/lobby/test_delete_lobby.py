import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.db.base import Lobby

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup


class BaseTestDeleteLobby(BaseTestSetup):
    route = "/api/v1/lobby/{lobby_id}"

    async def _send_delete_request(self, client_async: AsyncClient, lobby: BaseObjectData[Lobby], headers: Optional[InputData] = None) -> Response:
        return await client_async.delete(self.route.format(lobby_id=lobby.id), headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestDeleteLobby(BaseTestDeleteLobby):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_delete_lobby_success(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, lobby, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == lobby.id, "Lobby ID does not match"
        assert f"Lobby '{lobby.data.name}' successfully removed" in json_data["description"], "Success message mismatch"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST_MODERATORS)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_delete_lobby_success_moderators(self,
            client_async: AsyncClient,
            lobby_other: BaseObjectData[Lobby],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, lobby_other, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == lobby_other.id, "Lobby ID does not match"
        assert f"Lobby '{lobby_other.data.name}' successfully removed" in json_data["description"], "Success message mismatch"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST_USER)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_delete_lobby_forbidden(self,
            client_async: AsyncClient,
            lobby_other: BaseObjectData[Lobby],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, lobby_other, base_user.headers)
        json_data = response.json()

        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "No access to control lobby" in json_data["detail"], f"Expected 'No access to control lobby', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_delete_lobby_not_found(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, lobby, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Lobby not found" in json_data["detail"], f"Expected error message 'Lobby not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True, False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_delete_lobby_unauthorized(self, client_async: AsyncClient, lobby: BaseObjectData[Lobby]):
        response = await self._send_delete_request(client_async, lobby)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
