import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.lobby.algorithm.models import Algorithm

from tests.utils.types import InputData
from tests.utils.constants import Roles
from tests.utils.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup

import tests.params.routes.lobby as params


class BaseTestCreateLobby(BaseTestSetup):
    route = "/api/v1/lobby/"

    async def _send_post_request(self, client_async: AsyncClient, json_data: InputData, headers: Optional[InputData] = None) -> Response:
        return await client_async.post(self.route, json=json_data, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestCreateLobby(BaseTestCreateLobby):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True])
    @pytest.mark.parametrize("input_data", params.LOBBY_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_create_lobby_success(self,
            client_async: AsyncClient,
            input_data: InputData,
            algorithm_other: BaseObjectData[Algorithm],
            base_user: BaseUserData
    ):
        lobby_data = input_data.copy()
        lobby_data["host_id"] = base_user.user.id
        lobby_data["algorithm_id"] = algorithm_other.id

        response = await self._send_post_request(client_async, lobby_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["name"] == lobby_data["name"], "Lobby name does not match"
        assert json_data["host"]["id"] == lobby_data["host_id"], "Host ID does not match"
        assert json_data["algorithm"]["id"] == lobby_data["algorithm_id"], "Algorithm ID does not match"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True, False])
    @pytest.mark.parametrize("input_data, expected_error", params.LOBBY_INVALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_create_lobby_invalid_data(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user: BaseUserData,
            input_data: InputData,
            expected_error: str
    ):
        lobby_data = input_data.copy()
        lobby_data["host_id"] = base_user.user.id
        lobby_data["algorithm_id"] = algorithm.id

        response = await self._send_post_request(client_async, lobby_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert expected_error in str(json_data["detail"]), f"Expected error '{expected_error}', got {json_data["detail"]}"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [False])
    @pytest.mark.parametrize("input_data", params.LOBBY_VALID_DATA)
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_create_lobby_algorithm_not_found(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user: BaseUserData,
            input_data: InputData
    ):
        lobby_data = input_data.copy()
        lobby_data["host_id"] = base_user.user.id
        lobby_data["algorithm_id"] = algorithm.id

        response = await self._send_post_request(client_async, lobby_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Algorithm not found" in json_data["detail"], f"Expected error message 'Algorithm not found', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_data", params.LOBBY_VALID_DATA)
    async def test_create_lobby_unauthorized(self, client_async: AsyncClient, input_data: InputData):
        response = await self._send_post_request(client_async, input_data)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
