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
        ({"name": "New Lobby"}, 200,    ""),
        ({"name": "   "},       422,    "name cannot be empty"),
    ]
)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_create_lobby(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        test_algorithm_id: int,
        lobby_data: InputData,
        expected_status: int,
        error_substr: str,
        role: UserRole
):

    route = "/api/v1/lobby/"
    user, headers = await test_base_user_from_role(role)
    lobby_data["host_id"] = user.id
    lobby_data["algorithm_id"] = test_algorithm_id

    response: Response = await client_async.post(route, json=lobby_data, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if expected_status == 200:
        assert json_data["name"] == lobby_data["name"], "Lobby name does not match"
    else:
        assert error_substr in json_data["detail"][0]["msg"], f"Message doesn't contains substring: {json_data["detail"][0]["msg"]}"


@pytest.mark.asyncio
@pytest.mark.parametrize("update_data", [{"name": "New Lobby"}])
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status",
    [
        (UserRole.ADMIN,        False,  200),
        (UserRole.MODERATOR,    False,  200),
        (UserRole.USER,         True,   200),
        (UserRole.USER,         False,  403),
    ]
)
async def test_update_lobby(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status: int,
        update_data: InputData
):

    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    lobby_id, _ = await test_create_lobby_from_data(user if is_lobby_owner else creator)
    
    route = f"/api/v1/lobby/{lobby_id}"
    response: Response = await client_async.put(route, json=update_data, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status == 200:
        json_data = response.json()
        assert json_data["name"] == update_data["name"], "Lobby name was not updated"
        assert json_data["status"] == LobbyStatus.ACTIVE, f"Lobby status isn't Active, got {json_data["status"]}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status",
    [
        (UserRole.ADMIN,        False,  200),
        (UserRole.MODERATOR,    False,  200),
        (UserRole.USER,         True,   200),
        (UserRole.USER,         False,  403),
    ]
)
async def test_close_lobby(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status: int,
):

    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    lobby_id, _ = await test_create_lobby_from_data(user if is_lobby_owner else creator)
    
    route = f"/api/v1/lobby/{lobby_id}/close"
    response: Response = await client_async.put(route, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status == 200:
        json_data = response.json()
        assert json_data["status"] == LobbyStatus.ARCHIVED, f"Lobby status isn't Archived, got {json_data["status"]}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status",
    [
        (UserRole.ADMIN,        False,  200),
        (UserRole.MODERATOR,    False,  200),
        (UserRole.USER,         True,   200),
        (UserRole.USER,         False,  403),
    ]
)
async def test_delete_lobby(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status: int,
):

    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    lobby_id, lobby = await test_create_lobby_from_data(user if is_lobby_owner else creator)
    route = f"/api/v1/lobby/{lobby_id}"

    response: Response = await client_async.delete(route, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status == 200:
        json_data = response.json()
        assert json_data["id"] == lobby_id, f"Expected {lobby_id}, got {json_data["id"]}"
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
