import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.lobby.algorithm.models import Algorithm
from app.modules.lobby.lobby.models import Lobby
from app.modules.lobby.participant.models import LobbyParticipant
from app.modules.lobby.team.models import Team

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup

import tests.params.routes.lobby as params


class BaseTestUpdateLobby(BaseTestSetup):
    route = "/api/v1/lobby/{lobby_id}"

    async def _send_put_request(self, client_async: AsyncClient, lobby: BaseObjectData[Lobby], json_data: InputData, headers: Optional[InputData] = None) -> Response:
        return await client_async.put(self.route.format(lobby_id=lobby.id), json=json_data, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestUpdateLobby(BaseTestUpdateLobby):
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("update_data", params.LOBBY_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_update_lobby_success(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, lobby, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == lobby.id, "Lobby ID does not match"
    
        if "name" in update_data:
            assert json_data["name"] == update_data["name"], "Lobby name was not updated"

        if "status" in update_data:
            assert json_data["status"] == update_data["status"], "Lobby status was not updated"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True])
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("update_data", params.LOBBY_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_update_lobby_algorithm_success(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            algorithm_other: BaseObjectData[Algorithm],
            base_user: BaseUserData,
            update_data: InputData
    ):
        lobby_data = update_data.copy()
        lobby_data["algorithm_id"] = algorithm_other.id

        response = await self._send_put_request(client_async, lobby, lobby_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == lobby.id, "Lobby ID does not match"
    
        if "name" in update_data:
            assert json_data["name"] == update_data["name"], "Lobby name was not updated"

        if "status" in update_data:
            assert json_data["status"] == update_data["status"], "Lobby status was not updated"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("update_data", params.LOBBY_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_update_lobby_host_success(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            base_user: BaseUserData,
            base_user_other: BaseUserData,
            update_data: InputData
    ):
        lobby_data = update_data.copy()
        lobby_data["host_id"] = base_user_other.user.id

        response = await self._send_put_request(client_async, lobby, lobby_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["host"]["id"] == base_user_other.user.id, "Host ID does not match"
    
        if "name" in update_data:
            assert json_data["name"] == update_data["name"], "Lobby name was not updated"

        if "status" in update_data:
            assert json_data["status"] == update_data["status"], "Lobby status was not updated"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("update_data, error_substr", params.LOBBY_INVALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_update_lobby_invalid_data(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            base_user: BaseUserData,
            update_data: InputData,
            error_substr: str
    ):
        response = await self._send_put_request(client_async, lobby, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert error_substr in str(json_data["detail"]), f"Expected error '{error_substr}', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("update_data", params.LOBBY_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST_USER)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_update_lobby_forbidden(self,
            client_async: AsyncClient,
            lobby_other: BaseObjectData[Lobby],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, lobby_other, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "No access to control lobby" in json_data["detail"], f"Expected 'No access to control lobby', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [False])
    @pytest.mark.parametrize("update_data", params.LOBBY_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_update_lobby_not_found(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, lobby, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Lobby not found" in json_data["detail"], f"Expected error message 'Lobby not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True, False])
    @pytest.mark.parametrize("update_data", params.LOBBY_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_update_lobby_unauthorized(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, lobby, update_data)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
