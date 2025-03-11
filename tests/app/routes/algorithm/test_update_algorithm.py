import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import Algorithm

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData, BaseObjectData
from tests.classes.setup import BaseTestSetup

import tests.params.routes.algorithm as params


class BaseTestUpdateAlgorithm(BaseTestSetup):
    route = "/api/v1/algorithm/{algorithm_id}"

    async def _send_put_request(self, client_async: AsyncClient, algorithm: BaseObjectData[Algorithm], json_data: InputData, headers: InputData | None = None) -> Response:
        return await client_async.put(self.route.format(algorithm_id=algorithm.id), json=json_data, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestUpdateAlgorithm(BaseTestUpdateAlgorithm):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("update_data", params.ALGORITHM_VALID_UPDATE_DATA)
    async def test_update_algorithm_success(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, algorithm, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == algorithm.id, "Algorithm ID does not match"
        
        if "name" in update_data:
            assert json_data["name"] == update_data["name"], "Algorithm name was not updated"

        if "algorithm" in update_data:
            assert json_data["algorithm"] == update_data["algorithm"], "Algorithm code was not updated"
            assert json_data["teams_count"] == update_data["teams_count"], "Algorithm teams count was not updated"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("role_other", Roles.LIST_MODERATORS)
    @pytest.mark.parametrize("update_data", params.ALGORITHM_VALID_UPDATE_DATA)
    async def test_update_algorithm_success_moderators(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user_other: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, algorithm, update_data, base_user_other.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["id"] == algorithm.id, "Algorithm ID does not match"
        
        if "name" in update_data:
            assert json_data["name"] == update_data["name"], "Algorithm name was not updated"

        if "algorithm" in update_data:
            assert json_data["algorithm"] == update_data["algorithm"], "Algorithm code was not updated"
            assert json_data["teams_count"] == update_data["teams_count"], "Algorithm teams count was not updated"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("update_data, error_substr", params.ALGORITHM_INVALID_DATA)
    async def test_update_algorithm_invalid_data(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user: BaseUserData,
            update_data: InputData,
            error_substr: str
    ):
        response = await self._send_put_request(client_async, algorithm, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert error_substr in str(json_data["detail"]), f"Expected error '{error_substr}', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [True])
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("role_other", Roles.LIST_USER)
    @pytest.mark.parametrize("update_data", params.ALGORITHM_VALID_UPDATE_DATA)
    async def test_update_algorithm_forbidden(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user_other: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, algorithm, update_data, base_user_other.headers)
        json_data = response.json()
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "No access to control algorithm" in json_data["detail"], f"Expected 'No access to control algorithm', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("algorithm_exists", [False])
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("update_data", params.ALGORITHM_VALID_UPDATE_DATA)
    async def test_update_algorithm_not_found(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, algorithm, update_data, base_user.headers)
        json_data = response.json()
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "Algorithm not found" in json_data["detail"], f"Expected error message 'Algorithm not found', got: '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("algorithm_exists", [True, False])
    @pytest.mark.parametrize("update_data", params.ALGORITHM_FIELD_REQUIRED)
    async def test_update_algorithm_field_required(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            base_user: BaseUserData,
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, algorithm, update_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert "Field required" in str(json_data["detail"]), f"Expected error 'Field required', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("role", Roles.LIST)
    @pytest.mark.parametrize("algorithm_exists", [True, False])
    @pytest.mark.parametrize("update_data", params.ALGORITHM_VALID_UPDATE_DATA)
    async def test_update_algorithm_unauthorized(self,
            client_async: AsyncClient,
            algorithm: BaseObjectData[Algorithm],
            update_data: InputData
    ):
        response = await self._send_put_request(client_async, algorithm, update_data)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
