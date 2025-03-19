import pytest

from fastapi import Response

from httpx import AsyncClient

from tests.utils.types import InputData
from tests.factories.user_factory import UserFactory
from tests.factories.general_factory import GeneralFactory
from tests.classes.setup import BaseTestSetup

import tests.params.routes.auth as params


class BaseTestLoginUser(BaseTestSetup):
    route = "/api/v1/auth/login"

    async def _send_post_request(self, client_async: AsyncClient, form_data: InputData) -> Response:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return await client_async.post(self.route, data=form_data, headers=headers)


    @pytest.fixture
    async def existing_user(self, user_factory: UserFactory, user_register_data: InputData) -> InputData:
        await user_factory.create_from_data(user_register_data)
        return {"username": user_register_data["username"], "password": user_register_data["password"]}
    

    @pytest.fixture
    async def logged_in_user(self, general_factory: GeneralFactory) -> InputData:
        user = await general_factory.create_base_user(password="SecurePassword123!")
        return {"username": user.user.username, "password": "SecurePassword123!"}


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("general_factory")
class TestLoginUser(BaseTestLoginUser):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_register_data", params.REGISTER_USER_VALID_DATA)
    async def test_login_success(self, client_async: AsyncClient, user_register_data: InputData, existing_user: InputData):
        response = await self._send_post_request(client_async, existing_user)
        json_data = response.json()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "access_token" in json_data, "Response should contain access_token"
        assert "refresh_token" in json_data, "Response should contain refresh_token"


    @pytest.mark.asyncio
    async def test_login_already_logged_in(self, client_async: AsyncClient, logged_in_user: InputData):
        response = await self._send_post_request(client_async, logged_in_user)
        json_data = response.json()

        assert response.status_code == 409, f"Expected 409, got {response.status_code}"
        assert "User is already logged in" in json_data["detail"], f"Expected error 'User is already logged in', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("form_data, error_message", params.LOGIN_USER_INVALID_DATA)
    async def test_login_invalid_form(self, client_async: AsyncClient, form_data: InputData, error_message: str):
        response = await self._send_post_request(client_async, form_data)
        json_data = response.json()

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert error_message in str(json_data["detail"]), f"Expected error '{error_message}', got '{json_data["detail"]}'"


    @pytest.mark.asyncio
    @pytest.mark.parametrize("form_data", params.LOGIN_USER_VALID_DATA)
    async def test_login_non_existant_users(self, client_async: AsyncClient, form_data: InputData):
        response = await self._send_post_request(client_async, form_data)
        json_data = response.json()

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        assert json_data["detail"] == "Incorrect username or password", f"Expect 'Incorrect username or password', got '{json_data["detail"]}'"
    