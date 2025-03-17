import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.db.base import Lobby, LobbyParticipant, Team

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup


class BaseTestAddParticipant(BaseTestSetup):
    route = "/api/v1/lobby/{lobby_id}/participants"

    def get_params_from_user(self, user: Optional[BaseUserData] = None):
        if user:
            return {"user_id": user.user.id}
        return {"user_id": -1}

    async def _send_post_request(self,
        client_async: AsyncClient,
        lobby: BaseObjectData[Lobby],
        team: BaseObjectData[Team],
        user: Optional[BaseUserData] = None,
        headers: Optional[InputData] = None
    ) -> Response:
        params = self.get_params_from_user(user)
        
        if team.data:
            params["team_id"] = team.id

        return await client_async.post(self.route.format(lobby_id=lobby.id), params=params, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestAddParticipant(BaseTestAddParticipant):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True, False])
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_add_participant_success(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            team: BaseObjectData[Team],
            base_user: BaseUserData,
            base_user_other: BaseUserData,
    ):
        response = await self._send_post_request(client_async, lobby, team, base_user_other, headers=base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["user"]["id"] == base_user_other.user.id, "User ID does not match"
        assert json_data["lobby"]["id"] == lobby.id, "Lobby ID does not match"

        if team.data:
            assert json_data["team"]["id"] == team.id, "Team ID does not match"
        else:
            assert json_data["team"] is None, "Team does not match"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True, False])
    @pytest.mark.parametrize("role", Roles.LIST_MODERATORS)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_add_participant_success_moderators(self,
            client_async: AsyncClient,
            lobby_other: BaseObjectData[Lobby],
            team_other: BaseObjectData[Team],
            base_user: BaseUserData,
            base_user_other: BaseUserData,
    ):
        response = await self._send_post_request(client_async, lobby_other, team_other, base_user_other, headers=base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["user"]["id"] == base_user_other.user.id, "User ID does not match"
        assert json_data["lobby"]["id"] == lobby_other.id, "Lobby ID does not match"

        if team_other.data:
            assert json_data["team"]["id"] == team_other.id, "Team ID does not match"
        else:
            assert json_data["team"] is None, "Team does not match"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True, False])
    @pytest.mark.parametrize("role", Roles.LIST_USER)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_add_participant_forbidden(self,
            client_async: AsyncClient,
            lobby_other: BaseObjectData[Lobby],
            team_other: BaseObjectData[Team],
            base_user: BaseUserData,
            base_user_other: BaseUserData,
    ):
        response = await self._send_post_request(client_async, lobby_other, team_other, base_user_other, headers=base_user.headers)
        json_data = response.json()

        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "No access to control lobby" in json_data["detail"], f"Expected 'No access to control lobby', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [False])
    @pytest.mark.parametrize("team_exists", [False])
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_add_participant_lobby_not_found(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            team: BaseObjectData[Team],
            base_user: BaseUserData,
            base_user_other: BaseUserData
    ):
        response = await self._send_post_request(client_async, lobby, team, base_user_other, headers=base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Lobby not found" in json_data["detail"], f"Expected error message 'Lobby not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [False])
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_add_participant_team_not_found(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            team: BaseObjectData[Team],
            base_user: BaseUserData,
            base_user_other: BaseUserData
    ):
        team.data = True
        response = await self._send_post_request(client_async, lobby, team, base_user_other, headers=base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Team not found" in json_data["detail"], f"Expected error message 'Team not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True, False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_add_participant_user_not_found(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            team: BaseObjectData[Team],
            base_user: BaseUserData
    ):
        response = await self._send_post_request(client_async, lobby, team, headers=base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "User not found" in json_data["detail"], f"Expected error message 'User not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("team_exists", [True, False])
    @pytest.mark.parametrize("participant_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_add_participant_already_in_lobby(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            team: BaseObjectData[Team],
            participant: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData
    ):
        exist_participant = BaseUserData(participant.data.user, "", "", {})
        response = await self._send_post_request(client_async, lobby, team, exist_participant, headers=base_user.headers)
        json_data = response.json()

        assert response.status_code == 409, f"Expected 409, got {response.status_code}"
        assert "User already in lobby" in json_data["detail"], f"Expected error message 'User already in lobby', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True, False])
    @pytest.mark.parametrize("team_exists", [True, False])
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_add_participant_unauthorized(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            team: BaseObjectData[Team],
            base_user_other: BaseUserData
    ):
        response = await self._send_post_request(client_async, lobby, team, base_user_other)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
