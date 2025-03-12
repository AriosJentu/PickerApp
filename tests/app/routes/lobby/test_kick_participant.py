import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import Lobby, LobbyParticipant

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup


class BaseTestKickParticipant(BaseTestSetup):
    route = "/api/v1/lobby/{lobby_id}/participants/{participant_id}"

    async def _send_delete_request(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            participant: BaseObjectData[LobbyParticipant],
            headers: InputData | None = None
    ) -> Response:
        return await client_async.delete(self.route.format(lobby_id=lobby.id, participant_id=participant.id), headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestKickParticipant(BaseTestKickParticipant):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("participant_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_kick_participant_success(self,
            client_async,
            lobby: BaseObjectData[Lobby],
            participant: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, lobby, participant, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["user"]["id"] == participant.data.user.id, "User ID does not match"
        assert json_data["lobby"]["id"] == lobby.id, "Lobby ID does not match"
    
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("participant_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST_MODERATORS)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_kick_participant_success_moderators(self,
            client_async,
            lobby_other: BaseObjectData[Lobby],
            participant_lobby_other: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, lobby_other, participant_lobby_other, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["user"]["id"] == participant_lobby_other.data.user.id, "User ID does not match"
        assert json_data["lobby"]["id"] == lobby_other.id, "Lobby ID does not match"

    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("participant_exists", [True, False])
    @pytest.mark.parametrize("role", Roles.LIST_USER)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_kick_participant_forbidden(self,
            client_async,
            lobby_other: BaseObjectData[Lobby],
            participant_lobby_other: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, lobby_other, participant_lobby_other, base_user.headers)
        json_data = response.json()

        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "No access to control lobby" in json_data["detail"], f"Expected 'No access to control lobby', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [False])
    @pytest.mark.parametrize("participant_exists", [True, False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_kick_participant_lobby_not_found(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            participant: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData 
    ):
        response = await self._send_delete_request(client_async, lobby, participant, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Lobby not found" in json_data["detail"], f"Expected error message 'Lobby not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("participant_exists", [False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_kick_participant_not_found(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            participant: BaseObjectData[LobbyParticipant],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, lobby, participant, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Participant not found" in json_data["detail"], f"Expected error message 'Participant not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("lobby_exists", [True])
    @pytest.mark.parametrize("participant_exists", [False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_kick_participant_unauthorized(self,
            client_async: AsyncClient,
            lobby: BaseObjectData[Lobby],
            participant: BaseObjectData[LobbyParticipant]
    ):
        response = await self._send_delete_request(client_async, lobby, participant)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
