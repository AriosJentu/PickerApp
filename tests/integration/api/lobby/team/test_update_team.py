import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.lobby.team.models import Team

from tests.test_config.classes.setup import BaseTestSetup
from tests.test_config.utils.constants import Roles
from tests.test_config.utils.dataclasses import BaseUserData, BaseObjectData
from tests.test_config.utils.types import InputData

import tests.test_config.params.routes.team as params


class BaseTestUpdateTeam(BaseTestSetup):
    route = "/api/v1/teams/{team_id}"

    async def _send_put_request(self, client_async: AsyncClient, team: BaseObjectData[Team], json_data: InputData, headers: Optional[InputData] = None) -> Response:
        return await client_async.put(self.route.format(team_id=team.id), json=json_data, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestUpdateTeam(BaseTestUpdateTeam):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True])
    @pytest.mark.parametrize("update_data", params.TEAM_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_update_team_success(self,
            client_async: AsyncClient,
            team: BaseObjectData[Team],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, team, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == team.id, "Team ID does not match"
        assert json_data["name"] == update_data["name"], "Team name was not updated"
   
   
    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True])
    @pytest.mark.parametrize("update_data", params.TEAM_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST_MODERATORS)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_update_team_success_moderators(self,
            client_async: AsyncClient,
            team_other: BaseObjectData[Team],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, team_other, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == team_other.id, "Team ID does not match"
        assert json_data["name"] == update_data["name"], "Team name was not updated"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True])
    @pytest.mark.parametrize("update_data, error_substr", params.TEAM_UPDATE_INVALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_update_team_invalid_data(self,
            client_async: AsyncClient,
            team: BaseObjectData[Team],
            base_user: BaseUserData,
            update_data: InputData,
            error_substr: str
    ):
        response = await self._send_put_request(client_async, team, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert error_substr in str(json_data["detail"]), f"Expected error '{error_substr}', got '{json_data["detail"]}'"

   
    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True])
    @pytest.mark.parametrize("update_data", params.TEAM_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST_USER)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_update_team_forbidden(self,
            client_async: AsyncClient,
            team_other: BaseObjectData[Team],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, team_other, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "No access to control team" in json_data["detail"], f"Expected 'No access to control team', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [False])
    @pytest.mark.parametrize("update_data", params.TEAM_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_update_team_not_found(self,
            client_async: AsyncClient,
            team: BaseObjectData[Team],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, team, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Team not found" in json_data["detail"], f"Expected error message 'Team not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True, False])
    @pytest.mark.parametrize("team_exists", [True, False])
    @pytest.mark.parametrize("update_data", params.TEAM_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_update_team_unauthorized(self,
            client_async: AsyncClient, 
            team: BaseObjectData[Team],
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, team, update_data)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
