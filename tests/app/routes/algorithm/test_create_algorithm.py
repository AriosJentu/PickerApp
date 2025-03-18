import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.auth.user.enums import UserRole

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData
from tests.classes.setup import BaseTestSetup

import tests.params.routes.algorithm as params


class BaseTestCreateAlgorithm(BaseTestSetup):
    route = "/api/v1/algorithm/"

    async def _send_post_request(self, client_async: AsyncClient, json_data: InputData, headers: Optional[InputData] = None) -> Response:
        return await client_async.post(self.route, json=json_data, headers=headers or {})


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
@pytest.mark.parametrize("role", Roles.LIST)
class TestCreateAlgorithm(BaseTestCreateAlgorithm):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_data", params.ALGORITHM_VALID_DATA)
    async def test_create_algorithm_success(self,
            client_async: AsyncClient,
            base_user: BaseUserData,
            input_data: InputData
    ):
        algorithm_data = input_data.copy()
        algorithm_data["creator_id"] = base_user.user.id

        response = await self._send_post_request(client_async, algorithm_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert json_data["name"] == input_data["name"], "Algorithm name does not match"
        assert json_data["algorithm"] == input_data["algorithm"], "Algorithm script does not match"
        assert json_data["teams_count"] == input_data["teams_count"], "Teams count does not match"
        assert json_data["creator"]["id"] == base_user.user.id, "Algorithm creator does not match"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_data, expected_error", params.ALGORITHM_INVALID_DATA)
    async def test_create_algorithm_invalid_data(self,
            client_async: AsyncClient,
            base_user: BaseUserData,
            input_data: InputData,
            expected_error: str
    ):
        
        algorithm_data = input_data.copy()
        algorithm_data["creator_id"] = base_user.user.id

        response = await self._send_post_request(client_async, algorithm_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert expected_error in str(json_data["detail"]), f"Expected error '{expected_error}', got {json_data["detail"]}"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_data", params.ALGORITHM_FIELD_REQUIRED)
    async def test_create_algorithm_invalid_data_field_required(self,
            client_async: AsyncClient,
            base_user: BaseUserData,
            input_data: InputData
    ):
        
        algorithm_data = input_data.copy()
        algorithm_data["creator_id"] = base_user.user.id

        response = await self._send_post_request(client_async, algorithm_data, base_user.headers)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert "Field required" in str(json_data["detail"]), f"Expected error 'Field required', got {json_data["detail"]}"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_data", params.ALGORITHM_VALID_DATA)
    async def test_create_algorithm_unauthorized(self, client_async: AsyncClient, input_data: InputData, role: UserRole):
        response = await self._send_post_request(client_async, input_data)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
