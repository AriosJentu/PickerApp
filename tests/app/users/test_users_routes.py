import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import User
from app.enums.user import UserRole

from tests.types import (
    BaseUserFixtureCallable, 
    BaseCreatorUsersFixtureCallable, 
    InputData, 
    RouteBaseFixture
)
from tests.constants import Roles, USERS_COUNT
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.test_lists import check_list_responces
from tests.utils.routes_utils import get_protected_routes
from tests.utils.common_fixtures import (
    test_base_user_from_role,
    test_base_creator_users_from_role,
    protected_route
)


all_routes = [
    ("GET",     "/api/v1/users/list",       Roles.ALL_ROLES),
    ("GET",     "/api/v1/users/list-count", Roles.ALL_ROLES),
    ("GET",     "/api/v1/users/",           Roles.ALL_ROLES),
    ("PUT",     "/api/v1/users/",           Roles.ADMIN),
    ("DELETE",  "/api/v1/users/",           Roles.ADMIN),
    ("DELETE",  "/api/v1/users/tokens",     Roles.ADMIN),
]

default_search_user_data = [
    (True,  200,    "",                 {}),
    (False, 404,    "No data provided", {}),
    (False, 404,    "User not found",   {"get_user_id":     -1}),
    (False, 404,    "User not found",   {"get_username":    "someunexistantname"}),
    (False, 404,    "User not found",   {"get_email":       "unexistant@example.com"}),
]

default_roles_access = [
    (UserRole.USER,         403),
    (UserRole.MODERATOR,    403),
    (UserRole.ADMIN,        200),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_users_routes_access(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole
):
    await check_access_for_authenticated_users(client_async, protected_route, test_base_user_from_role, role)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
async def test_users_routes_require_auth(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
):
    await check_access_for_unauthenticated_users(client_async, protected_route)


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize(
    "query_params, expected_status, should_exist, error_substr",
    [
        ({"get_user_id":    1},                         200,    True,   ""),
        ({"get_username":   "testuser"},                200,    True,   ""),
        ({"get_email":      "testuser@example.com"},    200,    True,   ""),
        ({"get_user_id":    999},                       404,    False,  "User not found"),
        ({"get_username":   "nonexistent"},             404,    False,  "User not found"),
        ({"get_email":      "noemail@example.com"},     404,    False,  "User not found"),
    ]
)
async def test_get_user_by_data(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        query_params: InputData,
        expected_status: int,
        should_exist: bool,
        error_substr: str,
        role: UserRole
):
    route = "/api/v1/users/"
    user, headers = await test_base_user_from_role(role)

    response: Response = await client_async.get(route, headers=headers, params=query_params)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if should_exist:
        json_data = response.json()
        assert json_data["id"] == user.id, "Returned user ID does not match"
    else:
        assert error_substr in response.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_status, error_substr",
    [
        ({"email":          "new_email@example.com"},                   200, ""),
        ({"username":       "somenewname"},                             200, ""),
        ({"password":       "NewPassword123!"},                         200, ""),
        ({"username":       ""},                                        422, "Username must be at least 3 characters long."),
        ({"password":       "InvalidPassword"},                         422, "Password must contain"),
        ({"email":          "invalid-email"},                           422, "Invalid email format"),
    ]
)
@pytest.mark.parametrize("role, expected_status_access", default_roles_access)
@pytest.mark.parametrize("is_user_exist, expected_status_exists, error_substr_exists, user_params", default_search_user_data)
async def test_update_user(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        update_data: InputData,
        user_params: InputData,
        expected_status: int,
        expected_status_access: int,
        expected_status_exists: int,
        is_user_exist: bool,
        error_substr: str,
        error_substr_exists: str,
        role: UserRole
):
    route = "/api/v1/users/"
    
    _, headers, updatable_user, _ = await test_base_creator_users_from_role(role)
    if is_user_exist:
        user_params["get_user_id"] = updatable_user.id

    response: Response = await client_async.put(route, headers=headers, json=update_data, params=user_params)
    json_data = response.json()

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        return

    if expected_status != 200:
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        assert error_substr in str(json_data["detail"]), f"Details not containing info '{error_substr}'"
        return

    assert response.status_code == expected_status_exists, f"Expected {expected_status}, got {response.status_code}"

    if is_user_exist:
        if "email" in update_data:
            assert json_data["email"] == update_data["email"], "Email was not updated"
        
        if "username" in update_data:
            assert json_data["username"] == update_data["username"], "Email was not updated"
    else:
        assert error_substr_exists in json_data["detail"], f"Details not containing info '{error_substr_exists}'"


@pytest.mark.asyncio
@pytest.mark.parametrize("role, expected_status_access", default_roles_access)
@pytest.mark.parametrize("is_user_exist, expected_status_exists, error_substr_exists, user_params", default_search_user_data)
async def test_delete_user(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        user_params: InputData,
        expected_status_access: int,
        expected_status_exists: int,
        error_substr_exists: str,
        is_user_exist: bool,
        role: UserRole,
):

    route = "/api/v1/users/"
    _, headers, deletable_user, _ = await test_base_creator_users_from_role(role)
    if is_user_exist:
        user_params["get_user_id"] = deletable_user.id

    response: Response = await client_async.delete(route, headers=headers, params=user_params)
    json_data = response.json()

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        return

    assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
    if expected_status_exists != 200:
        assert error_substr_exists in str(json_data["detail"]), f"Details not containing info '{error_substr_exists}'"
        return

    # assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert json_data["id"] == deletable_user.id, "Deleted user ID does not match"
    assert json_data["username"] == deletable_user.username, "Deleted user username does not match"
    assert json_data["email"] == deletable_user.email, "Deleted user email does not match"
    assert json_data["detail"] == f"User with ID {deletable_user.id} has been deleted", "Unexpected delete confirmation message"


@pytest.mark.asyncio
@pytest.mark.parametrize("role, expected_status_access", default_roles_access)
@pytest.mark.parametrize("is_user_exist, expected_status_exists, error_substr_exists, user_params", default_search_user_data)
async def test_clear_user_tokens(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        role: UserRole,
        expected_status_access: int,
        is_user_exist: bool,
        expected_status_exists: int,
        error_substr_exists: str,
        user_params: InputData
):

    route = "/api/v1/users/tokens"

    _, headers, updatable_user, _ = await test_base_creator_users_from_role(role)
    if is_user_exist:
        user_params["get_user_id"] = updatable_user.id

    response: Response = await client_async.delete(route, headers=headers, params=user_params)
    json_data = response.json()
    
    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        return

    if expected_status_exists != 200:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_substr_exists in str(json_data["detail"]), f"Details not containing info '{error_substr_exists}'"
        return

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    assert json_data["id"] == updatable_user.id, "User ID does not match"
    assert json_data["username"] == updatable_user.username, "Username does not match"
    assert json_data["email"] == updatable_user.email, "Email does not match"
    assert json_data["detail"] == f"Tokens for user with ID {updatable_user.id} has been deactivated", "Unexpected response message"


filter_data_multiple = [
    (None,                                      USERS_COUNT+1),
    ({"id":         1},                         1),
    ({"username":   "testuser"},                USERS_COUNT+1),
    ({"sort_by":    "id"},                      USERS_COUNT+1),
    ({"sort_order": "desc"},                    USERS_COUNT+1),
    ({"limit":      2},                         2),
    ({"offset":     1},                         USERS_COUNT),
]

filter_data_default = [
    (None,                                      4),
    ({"id":         1},                         1),
    ({"role":       UserRole.USER.value},       2),
    ({"role":       UserRole.ADMIN.value},      1),
    ({"username":   "default"},                 1),
    ({"email":      "moderator@example.com"},   1),
    ({"sort_by":    "id"},                      4),
    ({"sort_order": "desc"},                    4),
    ({"limit":      2},                         2),
    ({"offset":     1},                         3),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data_multiple)
async def test_get_users_list_with_filters_multiple(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        create_multiple_test_users_with_tokens: list[tuple[User, str]],
        role: UserRole,
        filter_params: InputData,
        expected_count: int
):
    
    route = "/api/v1/users/list"
    await check_list_responces(
        client_async, test_base_user_from_role, role, route, 
        expected_count=expected_count,
        is_total_count=False, 
        filter_params=filter_params,
        obj_type="users"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("filter_params, expected_count", filter_data_default)
async def test_get_users_list_with_filters_default(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        create_test_users: list[User],
        filter_params: InputData,
        expected_count: int
):
    
    route = "/api/v1/users/list"
    await check_list_responces(
        client_async, test_base_user_from_role, UserRole.USER, route, 
        expected_count=expected_count,
        is_total_count=False, 
        filter_params=filter_params,
        obj_type="users"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data_multiple)
async def test_get_users_list_count_with_filters_multiple(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        create_multiple_test_users_with_tokens: list[tuple[User, str]],
        role: UserRole,
        filter_params: InputData,
        expected_count: int
):
    
    route = "/api/v1/users/list-count"
    await check_list_responces(
        client_async, test_base_user_from_role, role, route, 
        expected_count=expected_count,
        is_total_count=True, 
        filter_params=filter_params,
        obj_type="users"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("filter_params, expected_count", filter_data_default)
async def test_get_users_list_count_with_filters_default(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        create_test_users: list[User],
        filter_params: InputData,
        expected_count: int
):
    
    route = "/api/v1/users/list-count"
    await check_list_responces(
        client_async, test_base_user_from_role, UserRole.USER, route, 
        expected_count=expected_count,
        is_total_count=True, 
        filter_params=filter_params,
        obj_type="users"
    )
