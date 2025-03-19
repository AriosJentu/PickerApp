import pytest

from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.modules.auth.user.models import User

from tests.types import InputData
from tests.constants import Roles
from tests.dataclasses import BaseUserData
from tests.factories.general_factory import GeneralFactory
from tests.classes.setup import BaseTestSetup

import tests.params.routes.account as params


class BaseTestUpdateUser(BaseTestSetup):
    route = "/api/v1/account/"

    @pytest.fixture
    async def duplicate_user(self,
            general_factory: GeneralFactory,
            update_data: InputData,
            duplicate_email: bool,
            duplicate_username: bool,
            expected_status: int
    ) -> Optional[User]:
        
        duplicate_email = duplicate_email and "email" in update_data
        duplicate_username = duplicate_username and "username" in update_data
        return await general_factory.create_extra_user(update_data, duplicate_email, duplicate_username, expected_status == 422)


    async def _send_update_request(self,
            client_async: AsyncClient,
            base_user: BaseUserData,
            update_data: InputData
    ) -> Response:
        return await client_async.put(self.route, headers=base_user.headers, json=update_data)
    
    
    @pytest.fixture
    async def updated_user_token(self, 
            client_async: AsyncClient, 
            base_user: BaseUserData,
            update_data: InputData
    ) -> str:
        response = await self._send_update_request(client_async, base_user, update_data)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "access_token" in json_data, "Response does not contain access_token"

        return json_data["access_token"] 


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
@pytest.mark.parametrize("role", Roles.LIST)
class TestUpdateUser(BaseTestUpdateUser):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_data, error_substr", params.UPDATE_USER_DATA_INVALID)
    async def test_invalid_update_data(self,
            client_async: AsyncClient,
            base_user: BaseUserData,
            update_data: InputData,
            error_substr: str
    ):
        response: Response = await self._send_update_request(client_async, base_user, update_data)
        json_data = response.json()

        assert response.status_code == 422, f"Expected {422}, got {response.status_code}"
        assert error_substr in str(json_data["detail"]), f"Expected validation error '{error_substr}', got: '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_data", params.UPDATE_USER_DATA_DUPLICATES)
    @pytest.mark.parametrize("duplicate_username", [False])
    @pytest.mark.parametrize("duplicate_email, expected_status, error_substr", params.UPDATE_USER_DUPLICATE_EMAIL_EXPECT_ERROR)
    async def test_duplicate_email(self,
            client_async: AsyncClient,
            base_user: BaseUserData,
            duplicate_user: Optional[User],
            update_data: InputData,
            duplicate_email: bool,
            duplicate_username: bool,
            expected_status: int,
            error_substr: str
    ):
        response = await self._send_update_request(client_async, base_user, update_data)
        json_data = response.json()

        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        if expected_status != 200:
            assert error_substr in str(json_data["detail"]), f"Expected error '{error_substr}', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_data", params.UPDATE_USER_DATA_DUPLICATES)
    @pytest.mark.parametrize("duplicate_email", [False])
    @pytest.mark.parametrize("duplicate_username, expected_status, error_substr", params.UPDATE_USER_DUPLICATE_USERNAME_EXPECT_ERROR)
    async def test_duplicate_username(self,
            client_async: AsyncClient,
            base_user: BaseUserData,
            duplicate_user: Optional[User],
            update_data: InputData,
            duplicate_email: bool,
            duplicate_username: bool,
            expected_status: int,
            error_substr: str
    ):
        response = await self._send_update_request(client_async, base_user, update_data)
        json_data = response.json()

        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        if expected_status != 200:
            assert error_substr in str(json_data["detail"]), f"Expected error '{error_substr}', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_data", params.UPDATE_USER_DATA_VALID)
    async def test_successful_update(self,
            client_async: AsyncClient,
            update_data: InputData,
            updated_user_token: str
    ):
        assert updated_user_token is not None, "Access token was not received after update"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_data", params.UPDATE_USER_DATA_VALID)
    async def test_updated_user_data(self,
            client_async: AsyncClient,
            update_data: InputData,
            updated_user_token: str
    ):
        headers = {"Authorization": f"Bearer {updated_user_token}"}
        route = "/api/v1/account/"
        response: Response = await client_async.get(route, headers=headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        user_data = response.json()
        if "email" in update_data:
            assert user_data["email"] == update_data["email"], "Email was not updated"
        if "username" in update_data:
            assert user_data["username"] == update_data["username"], "Username was not updated"
