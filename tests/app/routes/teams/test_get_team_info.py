import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.lobby.team.models import Team

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup


class BaseTestGetTeam(BaseTestSetup):
    route = "/api/v1/teams/{team_id}"

    async def _send_get_request(self, client_async: AsyncClient, team: BaseObjectData[Team], headers: Optional[InputData] = None) -> Response:
        return await client_async.get(self.route.format(team_id=team.id), headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestGetTeam(BaseTestGetTeam):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_get_team_success(self,
            client_async: AsyncClient,
            team: BaseObjectData[Team],
            base_user: BaseUserData
    ):
        response = await self._send_get_request(client_async, team, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == team.id, "Team ID does not match"
        assert json_data["name"] == team.data.name, "Team name does not match"
        assert json_data["lobby"]["id"] == team.data.lobby_id, "Lobby ID does not match"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True, False])
    @pytest.mark.parametrize("team_exists", [False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_get_team_not_found(self,
            client_async: AsyncClient,
            team: BaseObjectData[Team],
            base_user: BaseUserData
    ):
        response = await self._send_get_request(client_async, team, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Team not found" in json_data["detail"], f"Expected error message 'Team not found', got: '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True, False])
    @pytest.mark.parametrize("team_exists", [True, False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_get_team_unauthorized(self, client_async: AsyncClient, team: BaseObjectData[Team]):
        response = await self._send_get_request(client_async, team)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
