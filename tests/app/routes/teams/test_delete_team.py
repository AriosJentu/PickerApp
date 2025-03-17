import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.db.base import Team

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup


class BaseTestDeleteTeam(BaseTestSetup):
    route = "/api/v1/teams/{team_id}"

    async def _send_delete_request(self, client_async: AsyncClient, team: BaseObjectData[Team], headers: Optional[InputData] = None) -> Response:
        return await client_async.delete(self.route.format(team_id=team.id), headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestDeleteTeam(BaseTestDeleteTeam):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_delete_team_success(self,
            client_async: AsyncClient,
            team: BaseObjectData[Team],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, team, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == team.id, "Team ID does not match"
        assert f"Team '{team.data.name}' deleted successfully" in json_data["description"], "Success message mismatch"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST_MODERATORS)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_delete_team_success_moderators(self,
            client_async: AsyncClient,
            team_other: BaseObjectData[Team],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, team_other, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == team_other.id, "Team ID does not match"
        assert f"Team '{team_other.data.name}' deleted successfully" in json_data["description"], "Success message mismatch"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST_USER)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_delete_team_forbidden(self,
            client_async: AsyncClient,
            team_other: BaseObjectData[Team],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, team_other, base_user.headers)
        json_data = response.json()

        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "No access to control team" in json_data["detail"], f"Expected 'No access to control team', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_delete_team_not_found(self,
            client_async: AsyncClient,
            team: BaseObjectData[Team],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, team, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Team not found" in json_data["detail"], f"Expected error message 'Team not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True, False])
    @pytest.mark.parametrize("team_exists", [True, False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_delete_team_unauthorized(self, client_async: AsyncClient, team: BaseObjectData[Team]):
        response = await self._send_delete_request(client_async, team)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
