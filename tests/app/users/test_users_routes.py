import pytest

from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.types import InputData
from tests.constants import Roles
from tests.classes.routes import BaseRoutesTest
from tests.classes.lists import BaseListsTest
from tests.factories.general_factory import GeneralFactory

import tests.params.routes.users as params
from tests.params.routes.common import get_role_status_response_for_admin_params
from tests.utils.routes_utils import get_protected_routes


@pytest.mark.usefixtures("client_async")
@pytest.mark.parametrize("protected_route", get_protected_routes(params.ROUTES), indirect=True)
class TestUserRoutes(BaseRoutesTest):
    pass


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("create_multiple_test_users_with_tokens")
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", params.USERS_FILTER_DATA_MULTIPLE)
class TestMultipleUsersLists(BaseListsTest):
    route = "/api/v1/users/list"
    route_count = "/api/v1/users/list-count"
    obj_type = "users"


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("create_test_users")
@pytest.mark.parametrize("role", [UserRole.USER])
@pytest.mark.parametrize("filter_params, expected_count", params.USERS_FILTER_DATA)
class TestBaseUsersLists(BaseListsTest):
    route = "/api/v1/users/list"
    route_count = "/api/v1/users/list-count"
    obj_type = "users"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("query_params, expected_status, should_exist, error_substr", params.USERS_PARAMS_STATUS_EXISTS_ERROR)
async def test_get_user_by_data(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        query_params: InputData,
        expected_status: int,
        should_exist: bool,
        error_substr: str,
        role: UserRole
):
    route = "/api/v1/users/"
    base_user_data = await general_factory.create_base_user(role)

    response: Response = await client_async.get(route, headers=base_user_data.headers, params=query_params)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if should_exist:
        json_data = response.json()
        assert json_data["id"] == base_user_data.user.id, "Returned user ID does not match"
    else:
        assert error_substr in response.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.parametrize("update_data, expected_status_update, error_substr_update", params.USERS_UPDATE_DATA_STATUS_ERROR)
@pytest.mark.parametrize("role, expected_status_access, error_substr_access", get_role_status_response_for_admin_params())
@pytest.mark.parametrize("is_user_exist, expected_status_exists, error_substr_exists, user_params", params.USERS_EXIST_STATUS_ERROR)
async def test_update_user(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        update_data: InputData,
        user_params: InputData,
        is_user_exist: bool,
        expected_status_update: int,
        expected_status_access: int,
        expected_status_exists: int,
        error_substr_update: str,
        error_substr_access: str,
        error_substr_exists: str,
        role: UserRole
):
    route = "/api/v1/users/"
    
    base_user_data, base_updatable_data = await general_factory.create_base_users_creator(role)
    if is_user_exist:
        user_params["get_user_id"] = base_updatable_data.user.id

    response: Response = await client_async.put(route, headers=base_user_data.headers, json=update_data, params=user_params)
    json_data = response.json()

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        assert error_substr_access in str(json_data["detail"]), f"Details not containing info '{error_substr_access}'"
        return

    if expected_status_update != 200:
        assert response.status_code == expected_status_update, f"Expected {expected_status_update}, got {response.status_code}"
        assert error_substr_update in str(json_data["detail"]), f"Details not containing info '{error_substr_update}'"
        return

    assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"

    if is_user_exist:
        if "email" in update_data:
            assert json_data["email"] == update_data["email"], "Email was not updated"
        
        if "username" in update_data:
            assert json_data["username"] == update_data["username"], "Email was not updated"
    else:
        assert error_substr_exists in json_data["detail"], f"Details not containing info '{error_substr_exists}'"


@pytest.mark.asyncio
@pytest.mark.parametrize("role, expected_status_access, error_substr_access", get_role_status_response_for_admin_params())
@pytest.mark.parametrize("is_user_exist, expected_status_exists, error_substr_exists, user_params", params.USERS_EXIST_STATUS_ERROR)
async def test_delete_user(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        user_params: InputData,
        is_user_exist: bool,
        expected_status_access: int,
        expected_status_exists: int,
        error_substr_access: str,
        error_substr_exists: str,
        role: UserRole,
):

    route = "/api/v1/users/"
    base_user_data, base_deletable_data = await general_factory.create_base_users_creator(role)
    if is_user_exist:
        user_params["get_user_id"] = base_deletable_data.user.id

    response: Response = await client_async.delete(route, headers=base_user_data.headers, params=user_params)
    json_data = response.json()

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        assert error_substr_access in str(json_data["detail"]), f"Details not containing info '{error_substr_access}'"
        return

    assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
    if expected_status_exists != 200:
        assert error_substr_exists in str(json_data["detail"]), f"Details not containing info '{error_substr_exists}'"
        return

    assert json_data["id"] == base_deletable_data.user.id, "Deleted user ID does not match"
    assert json_data["username"] == base_deletable_data.user.username, "Deleted user username does not match"
    assert json_data["email"] == base_deletable_data.user.email, "Deleted user email does not match"
    assert json_data["detail"] == f"User with ID {base_deletable_data.user.id} has been deleted", "Unexpected delete confirmation message"


@pytest.mark.asyncio
@pytest.mark.parametrize("role, expected_status_access, error_substr_access", get_role_status_response_for_admin_params())
@pytest.mark.parametrize("is_user_exist, expected_status_exists, error_substr_exists, user_params", params.USERS_EXIST_STATUS_ERROR)
async def test_clear_user_tokens(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        user_params: InputData,
        is_user_exist: bool,
        expected_status_access: int,
        expected_status_exists: int,
        error_substr_access: str,
        error_substr_exists: str,
        role: UserRole,
):

    route = "/api/v1/users/tokens"

    base_user_data, base_updatable_data = await general_factory.create_base_users_creator(role)
    if is_user_exist:
        user_params["get_user_id"] = base_updatable_data.user.id

    response: Response = await client_async.delete(route, headers=base_user_data.headers, params=user_params)
    json_data = response.json()
    
    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        assert error_substr_access in str(json_data["detail"]), f"Details not containing info '{error_substr_access}'"
        return

    if expected_status_exists != 200:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_substr_exists in str(json_data["detail"]), f"Details not containing info '{error_substr_exists}'"
        return

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    assert json_data["id"] == base_updatable_data.user.id, "User ID does not match"
    assert json_data["username"] == base_updatable_data.user.username, "Username does not match"
    assert json_data["email"] == base_updatable_data.user.email, "Email does not match"
    assert json_data["detail"] == f"Tokens for user with ID {base_updatable_data.user.id} has been deactivated", "Unexpected response message"
