import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.db.base import Algorithm

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup


class BaseTestDeleteAlgorithm(BaseTestSetup):
    route = "/api/v1/algorithm/{algorithm_id}"

    async def _send_delete_request(self, client_async: AsyncClient, algorithm: BaseObjectData[Algorithm], headers: Optional[InputData] = None) -> Response:
        return await client_async.delete(self.route.format(algorithm_id=algorithm.id), headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestDeleteAlgorithm(BaseTestDeleteAlgorithm):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_delete_algorithm_success(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, algorithm, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == algorithm.id, "Algorithm ID does not match"
        assert f"Algorithm '{algorithm.data.name}' deleted successfully" in json_data["description"], "Success message mismatch"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST_MODERATORS)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_delete_algorithm_success_moderators(self,
            client_async: AsyncClient,
            algorithm_other: BaseObjectData[Algorithm],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, algorithm_other, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == algorithm_other.id, "Algorithm ID does not match"
        assert f"Algorithm '{algorithm_other.data.name}' deleted successfully" in json_data["description"], "Success message mismatch"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST_USER)
    @pytest.mark.parametrize("role_other", Roles.LIST)
    async def test_delete_algorithm_forbidden(self,
            client_async: AsyncClient,
            algorithm_other: BaseObjectData[Algorithm],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, algorithm_other, base_user.headers)
        json_data = response.json()
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "No access to control algorithm" in json_data["detail"], f"Expected 'No access to control algorithm', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_delete_algorithm_not_found(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user: BaseUserData
    ):
        response = await self._send_delete_request(client_async, algorithm, base_user.headers)
        json_data = response.json()
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Algorithm not found" in json_data["detail"], f"Expected error message 'Algorithm not found', got: '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True, False])
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_delete_algorithm_unauthorized(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm]
    ):
        response = await self._send_delete_request(client_async, algorithm)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
