import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.db.base import Lobby

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup

import tests.params.routes.team as params


class BaseTestCreateTeam(BaseTestSetup):
    route = "/api/v1/teams/"

    async def _send_post_request(self, client_async, json_data: InputData, headers: Optional[InputData] = None) -> Response:
        return await client_async.post(self.route, json=json_data, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestCreateTeam(BaseTestCreateTeam):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("input_data", params.TEAM_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_create_team_success(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            base_user: BaseUserData,
            input_data: InputData
    ):
        team_data = input_data.copy()
        team_data["lobby_id"] = lobby.id

        response = await self._send_post_request(client_async, team_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["name"] == team_data["name"], "Team name does not match"
        assert json_data["lobby"]["id"] == team_data["lobby_id"], "Lobby ID does not match"
        

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("input_data", params.TEAM_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST_MODERATORS)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_create_team_success_moderators(self,
            client_async: AsyncClient,
            lobby_other: BaseObjectData[Lobby],
            base_user: BaseUserData,
            input_data: InputData
    ):
        team_data = input_data.copy()
        team_data["lobby_id"] = lobby_other.id

        response = await self._send_post_request(client_async, team_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["name"] == team_data["name"], "Team name does not match"
        assert json_data["lobby"]["id"] == team_data["lobby_id"], "Lobby ID does not match"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("input_data, expected_error", params.TEAM_INVALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_create_team_invalid_data(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            base_user: BaseUserData,
            input_data: InputData,
            expected_error: str
    ):
        team_data = input_data.copy()
        team_data["lobby_id"] = lobby.id

        response = await self._send_post_request(client_async, team_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert expected_error in str(json_data["detail"]), f"Expected error '{expected_error}', got {json_data["detail"]}"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("input_data", params.TEAM_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST_USER)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_create_team_forbidden(self,
            client_async: AsyncClient,
            lobby_other: BaseObjectData[Lobby],
            base_user: BaseUserData,
            input_data: InputData
    ):
        team_data = input_data.copy()
        team_data["lobby_id"] = lobby_other.id

        response = await self._send_post_request(client_async, team_data, base_user.headers)
        json_data = response.json()
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "No access to control team" in json_data["detail"], f"Expected 'No access to control team', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [False])
    @pytest.mark.parametrize("input_data", params.TEAM_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_create_team_not_found(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            base_user: BaseUserData,
            input_data: InputData
    ):
        team_data = input_data.copy()
        team_data["lobby_id"] = lobby.id

        response = await self._send_post_request(client_async, team_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Lobby not found" in json_data["detail"], f"Expected error message 'Lobby not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_data", params.TEAM_VALID_DATA)
    async def test_create_team_unauthorized(self, client_async: AsyncClient, input_data: InputData):
        response = await self._send_post_request(client_async, input_data)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
