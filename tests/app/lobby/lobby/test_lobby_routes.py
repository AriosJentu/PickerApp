import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import Lobby 
from app.enums.user import UserRole
from app.enums.lobby import LobbyStatus

from tests.types import (
    BaseObjectFixtureCallable,
    BaseUserFixtureCallable, 
    BaseCreatorUsersFixtureCallable, 
    InputData, 
    RouteBaseFixture
)
from tests.constants import Roles, LOBBIES_COUNT
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.test_lists import check_list_responces
from tests.utils.routes_utils import get_protected_routes
from tests.utils.common_fixtures import (
    test_base_user_from_role,
    test_base_creator_users_from_role,
    test_create_algorithm_from_data,
    test_create_lobby_from_data,
    protected_route
)


all_routes = [
    ("POST",    "/api/v1/lobby/",               Roles.ALL_ROLES),
    ("GET",     "/api/v1/lobby/list-count",     Roles.ALL_ROLES),
    ("GET",     "/api/v1/lobby/list",           Roles.ALL_ROLES),
    ("GET",     "/api/v1/lobby/1",              Roles.ALL_ROLES),
    ("PUT",     "/api/v1/lobby/1",              Roles.ALL_ROLES),
    ("PUT",     "/api/v1/lobby/1/close",        Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/lobby/1",              Roles.ALL_ROLES),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_lobbies_routes_access(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole
):
    await check_access_for_authenticated_users(client_async, protected_route, test_base_user_from_role, role)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
async def test_lobbies_routes_require_auth(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
):
    await check_access_for_unauthenticated_users(client_async, protected_route)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lobby_data, expected_status, error_substr",
    [
        ({"name":   "New Lobby"},   200,    ""),
        ({"name":   "   "},         422,    "Lobby name cannot be empty"),
        ({},                        422,    "Field required"),
    ]
)
@pytest.mark.parametrize(
    "algorithm_exists, expected_status_algorithm, error_algorithm_substr",
    [
        (True,  200,    ""),
        (False, 404,    "Algorithm not found"),
    ]
)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_create_lobby(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        test_create_algorithm_from_data: BaseObjectFixtureCallable,
        lobby_data: InputData,
        algorithm_exists: bool,
        expected_status: int,
        expected_status_algorithm: int,
        error_substr: str,
        error_algorithm_substr: str,
        role: UserRole
):

    route = "/api/v1/lobby/"
    user, headers = await test_base_user_from_role(role)
    algorithm_id, _ = await test_create_algorithm_from_data(user, algorithm_exists)

    lobby_data["host_id"] = user.id
    lobby_data["algorithm_id"] = algorithm_id

    response: Response = await client_async.post(route, json=lobby_data, headers=headers)

    json_data = response.json()
    if expected_status != 200:
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        message = json_data["detail"][0]["msg"]
        assert error_substr in str(message), f"Expected error '{error_substr}', got {message}"
        return
    
    assert response.status_code == expected_status_algorithm, f"Expected {expected_status_algorithm}, got {response.status_code}"
    if not algorithm_exists:
        assert error_algorithm_substr in str(json_data["detail"]), f"Expected error '{error_algorithm_substr}', got {json_data['detail']}"
        return

    assert json_data["name"] == lobby_data["name"], "Lobby name does not match"
    assert json_data["host"]["id"] == user.id, "User ID does not match"
    assert json_data["algorithm"]["id"] == algorithm_id, "Algorithm ID does not match"
    assert json_data["status"] == LobbyStatus.ACTIVE, "Lobby Status is not active"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lobby_exists, expected_status, error_substr",
    [
        (True,  200,    ""),
        (False, 404,    "Lobby not found"),
    ]
)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_lobby_info(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        lobby_exists: bool,
        expected_status: int,
        error_substr: str
):
    user, headers = await test_base_user_from_role(role)
    lobby_id, lobby = await test_create_lobby_from_data(user, lobby_exists)

    route = f"/api/v1/lobby/{lobby_id}"
    response: Response = await client_async.get(route, headers=headers)

    json_data = response.json()
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    if not lobby_exists:
        assert error_substr in str(json_data["detail"]), f"Expected '{error_substr}', got: {json_data['detail']}"
        return
    
    assert json_data["id"] == lobby_id, "Lobby ID does not match"
    assert json_data["host"]["id"] == user.id, "User ID does not match"
    assert json_data["algorithm"]["id"] == lobby.algorithm_id, "Algorithm ID does not match"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_status_update, error_substr_update",
    [
        ({"name":   "Updated Lobby"},               200,    ""),
        ({"status": LobbyStatus.ARCHIVED},          200,    ""),
        ({"name":   "   "},                         422,    "Lobby name cannot be empty"),
        ({},                                        400,    "Lobby update data not provided"),
    ]
)
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status_access, error_substr_access",
    [
        (UserRole.ADMIN,        False,  200,    ""),
        (UserRole.MODERATOR,    False,  200,    ""),
        (UserRole.USER,         True,   200,    ""),
        (UserRole.USER,         False,  403,    "No access to control lobby"),
    ]
)
@pytest.mark.parametrize(
    "lobby_exists, expected_status_lobby, error_substr_lobby",
    [
        (True,  200,    ""),
        (False, 404,    "Lobby not found"),
    ]
)
async def test_update_lobby(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        update_data: InputData,
        is_lobby_owner: bool,
        lobby_exists: bool,
        expected_status_update: int,
        expected_status_access: int,
        expected_status_lobby: int,
        error_substr_update: str,
        error_substr_access: str,
        error_substr_lobby: str,
        role: UserRole,
):

    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    lobby_id, _ = await test_create_lobby_from_data(user if is_lobby_owner else creator, lobby_exists)
    
    route = f"/api/v1/lobby/{lobby_id}"
    response: Response = await client_async.put(route, json=update_data, headers=headers)
    json_data = response.json()

    if expected_status_update == 422:
        assert response.status_code == expected_status_update, f"Expected {expected_status_update}, got {response.status_code}"
        assert error_substr_update in str(json_data["detail"]), f"Expected validation error '{error_substr_update}', got: {json_data['detail']}"
        return

    if not lobby_exists:
        assert response.status_code == expected_status_lobby, f"Expected {expected_status_lobby}, got {response.status_code}"
        assert error_substr_lobby in str(json_data["detail"]), f"Expected error '{error_substr_lobby}', got: {json_data['detail']}"
        return

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        assert error_substr_access in str(json_data["detail"]), f"Expected error '{error_substr_access}', got: {json_data['detail']}"
        return

    assert response.status_code == expected_status_update, f"Expected {expected_status_update}, got {response.status_code}"
    if expected_status_update == 400:
        assert error_substr_update in str(json_data["detail"]), f"Expected error '{error_substr_update}', got: {json_data['detail']}"
        return

    if "name" in update_data:
        assert json_data["name"] == update_data["name"], "Lobby name was not updated"
        assert json_data["status"] == LobbyStatus.ACTIVE, f"Lobby status isn't Active, got {json_data['status']}"
    
    if "status" in update_data:
        assert json_data["status"] == update_data["status"], f"Lobby status isn't {update_data["status"]}, got {json_data["status"]}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status_access, error_substr_access",
    [
        (UserRole.ADMIN,        False,  200,    ""),
        (UserRole.MODERATOR,    False,  200,    ""),
        (UserRole.USER,         True,   200,    ""),
        (UserRole.USER,         False,  403,    "No access to control lobby"),
    ]
)
@pytest.mark.parametrize(
    "lobby_exists, expected_status_lobby, error_substr_lobby",
    [
        (True,  200,    ""),
        (False, 404,    "Lobby not found"),
    ]
)
async def test_close_lobby(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        is_lobby_owner: bool,
        lobby_exists: bool,
        expected_status_access: int,
        expected_status_lobby: int,
        error_substr_access: str,
        error_substr_lobby: str
):

    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    lobby_id, _ = await test_create_lobby_from_data(user if is_lobby_owner else creator, lobby_exists)

    route = f"/api/v1/lobby/{lobby_id}/close"
    response: Response = await client_async.put(route, headers=headers)
    json_data = response.json()

    if not lobby_exists:
        assert response.status_code == expected_status_lobby, f"Expected {expected_status_lobby}, got {response.status_code}"
        assert error_substr_lobby in str(json_data["detail"]), f"Expected error '{error_substr_lobby}', got: {json_data['detail']}"
        return

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        assert error_substr_access in str(json_data["detail"]), f"Expected error '{error_substr_access}', got: {json_data['detail']}"
        return

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert json_data["status"] == LobbyStatus.ARCHIVED, f"Lobby status isn't Archived, got {json_data['status']}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status_access, error_substr_access",
    [
        (UserRole.ADMIN,        False,  200,    ""),
        (UserRole.MODERATOR,    False,  200,    ""),
        (UserRole.USER,         True,   200,    ""),
        (UserRole.USER,         False,  403,    "No access to control lobby"),
    ]
)
@pytest.mark.parametrize(
    "lobby_exists, expected_status_lobby, error_substr_lobby",
    [
        (True,  200,    ""),
        (False, 404,    "Lobby not found"),
    ]
)
async def test_delete_lobby(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        is_lobby_owner: bool,
        lobby_exists: bool,
        expected_status_access: int,
        expected_status_lobby: int,
        error_substr_access: str,
        error_substr_lobby: str
):

    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    lobby_id, lobby = await test_create_lobby_from_data(user if is_lobby_owner else creator, lobby_exists)

    route = f"/api/v1/lobby/{lobby_id}"
    response: Response = await client_async.delete(route, headers=headers)
    json_data = response.json()

    if not lobby_exists:
        assert response.status_code == expected_status_lobby, f"Expected {expected_status_lobby}, got {response.status_code}"
        assert error_substr_lobby in str(json_data["detail"]), f"Expected error '{error_substr_lobby}', got: {json_data['detail']}"
        return

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        assert error_substr_access in str(json_data["detail"]), f"Expected error '{error_substr_access}', got: {json_data['detail']}"
        return

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert json_data["id"] == lobby_id, f"Expected {lobby_id}, got {json_data['id']}"
    assert lobby.name in json_data["description"], f"Deleted lobby with incorrect name"


filter_data = [
    (None,                              LOBBIES_COUNT),
    ({"id":             1},             1),
    ({"name":           "2"},           1),
    ({"name":           "Test Lobby"},  LOBBIES_COUNT),
    ({"host_id":        0},             LOBBIES_COUNT),
    ({"host_id":        1},             0),
    ({"algorithm_id":   1},             LOBBIES_COUNT),
    ({"sort_by":        "id"},          LOBBIES_COUNT),
    ({"sort_order":     "desc"},        LOBBIES_COUNT),
    ({"limit":          2},             2),
    ({"offset":         1},             LOBBIES_COUNT-1),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data)
async def test_get_lobbies_list_with_filters(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        create_test_lobbies: list[Lobby],
        role: UserRole,
        filter_params: InputData,
        expected_count: int
):
    
    route = "/api/v1/lobby/list"
    await check_list_responces(
        client_async, test_base_user_from_role, role, route, 
        expected_count=expected_count,
        is_total_count=False, 
        filter_params=filter_params,
        obj_type="lobbies"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data)
async def test_get_lobbies_list_count_with_filters(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        create_test_lobbies: list[Lobby],
        role: UserRole,
        filter_params: InputData,
        expected_count: int
):
    
    route = "/api/v1/lobby/list-count"
    await check_list_responces(
        client_async, test_base_user_from_role, role, route, 
        expected_count=expected_count,
        is_total_count=True, 
        filter_params=filter_params,
        obj_type="lobbies"
    )
