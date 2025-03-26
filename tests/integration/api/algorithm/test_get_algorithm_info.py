import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.lobby.algorithm.models import Algorithm

from tests.test_config.classes.setup import BaseTestSetup
from tests.test_config.utils.constants import Roles
from tests.test_config.utils.dataclasses import BaseUserData, BaseObjectData
from tests.test_config.utils.types import InputData


class BaseTestGetAlgorithm(BaseTestSetup):
    route = "/api/v1/algorithm/{algorithm_id}"

    async def _send_get_request(self, client_async: AsyncClient, algorithm: BaseObjectData[Algorithm], headers: Optional[InputData] = None) -> Response:
        return await client_async.get(self.route.format(algorithm_id=algorithm.id), headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
@pytest.mark.parametrize("role", Roles.LIST)
class TestGetAlgorithm(BaseTestGetAlgorithm):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True])
    async def test_get_algorithm_success(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user: BaseUserData
    ):
        response = await self._send_get_request(client_async, algorithm, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == algorithm.id, "Algorithm ID does not match"
        assert json_data["name"] == algorithm.data.name, "Algorithm name does not match"
        assert json_data["algorithm"] == algorithm.data.algorithm, "Algorithm script does not match"
        assert json_data["teams_count"] == algorithm.data.teams_count, "Teams count does not match"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [False])
    async def test_get_algorithm_not_found(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user: BaseUserData
    ):
        response = await self._send_get_request(client_async, algorithm, base_user.headers)
        json_data = response.json()

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Algorithm not found" in json_data["detail"], f"Expected error message 'Algorithm not found', got: '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True, False])
    async def test_get_algorithm_unauthorized(self, client_async: AsyncClient, algorithm: BaseObjectData[Algorithm]):
        response = await self._send_get_request(client_async, algorithm)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
