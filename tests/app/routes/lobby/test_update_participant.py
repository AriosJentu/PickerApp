import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.lobby.lobby.models import Lobby
from app.modules.lobby.participant.models import LobbyParticipant
from app.modules.lobby.team.models import Team

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup

import tests.params.routes.lobby as params


class BaseTestEditParticipant(BaseTestSetup):
    route = "/api/v1/lobby/{lobby_id}/participants/{participant_id}"

    async def _send_put_request(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            participant: BaseObjectData[LobbyParticipant],
            json_data: InputData,
            headers: Optional[InputData] = None
    ) -> Response:
        return await client_async.put(self.route.format(lobby_id=lobby.id, participant_id=participant.id), json=json_data, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestEditParticipant(BaseTestEditParticipant):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("participant_exists", [True])
    @pytest.mark.parametrize("update_data", params.LOBBY_PARTICIPANT_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_edit_participant_success(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            participant: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, lobby, participant, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == participant.id, "Participant ID does not match"
        
        if "is_active" in update_data:
            assert json_data["is_active"] == update_data["is_active"], "Participant activity status was not updated"

        if "role" in update_data:
            assert json_data["role"] == update_data["role"], "Participant role was not updated"

        if "team_id" in update_data:
            if json_data["team"] is not None:
                assert json_data["team"]["id"] == update_data["team_id"], "Participant Team ID was not updated"
            else:
                assert json_data["team"] == None, "Participant Team was not updated"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("participant_exists", [True])
    @pytest.mark.parametrize("team_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_edit_participant_team_success(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            team: BaseObjectData[Team],
            participant: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData
    ):
        update_data = {"team_id": team.id}
        response = await self._send_put_request(client_async, lobby, participant, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == participant.id, "Participant ID does not match"
        assert json_data["team"]["id"] == update_data["team_id"], "Participant Team ID was not updated"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("participant_exists", [True])
    @pytest.mark.parametrize("update_data", params.LOBBY_PARTICIPANT_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST_MODERATORS)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_edit_participant_success_moderators(self,
            client_async: AsyncClient,
            lobby_other: BaseObjectData[Lobby],
            participant_lobby_other: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, lobby_other, participant_lobby_other, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == lobby_other.id, "Participant ID does not match"
        
        if "is_active" in update_data:
            assert json_data["is_active"] == update_data["is_active"], "Participant activity status was not updated"

        if "role" in update_data:
            assert json_data["role"] == update_data["role"], "Participant role was not updated"

        if "team_id" in update_data:
            if json_data["team"] is not None:
                assert json_data["team"]["id"] == update_data["team_id"], "Participant Team ID was not updated"
            else:
                assert json_data["team"] == None, "Participant Team was not updated"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("participant_exists", [True])
    @pytest.mark.parametrize("update_data, error_substr", params.LOBBY_PARTICIPANT_INVALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_edit_participant_invalid_data(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            participant: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData,
            update_data: InputData,
            error_substr: str
    ):
        response = await self._send_put_request(client_async, lobby, participant, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert error_substr in str(json_data["detail"]), f"Expected error '{error_substr}', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("participant_exists", [True])
    @pytest.mark.parametrize("update_data", params.LOBBY_PARTICIPANT_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST_USER)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_edit_participant_forbidden(self,
            client_async: AsyncClient,
            lobby_other: BaseObjectData[Lobby],
            participant_lobby_other: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, lobby_other, participant_lobby_other, update_data, base_user.headers)
        json_data = response.json()
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "No access to control lobby" in json_data["detail"], f"Expected 'No access to control lobby', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [False])
    @pytest.mark.parametrize("participant_exists", [True, False])
    @pytest.mark.parametrize("update_data", params.LOBBY_PARTICIPANT_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_edit_participant_lobby_not_found(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            participant: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, lobby, participant, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Lobby not found" in json_data["detail"], f"Expected error message 'Lobby not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("participant_exists", [False])
    @pytest.mark.parametrize("update_data", params.LOBBY_PARTICIPANT_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_edit_participant_not_found(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            participant: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, lobby, participant, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Participant not found" in json_data["detail"], f"Expected error message 'Participant not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True, False])
    @pytest.mark.parametrize("participant_exists", [True, False])
    @pytest.mark.parametrize("update_data", params.LOBBY_PARTICIPANT_VALID_UPDATE_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_edit_participant_unauthorized(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            participant: BaseObjectData[LobbyParticipant],
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, lobby, participant, update_data)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
