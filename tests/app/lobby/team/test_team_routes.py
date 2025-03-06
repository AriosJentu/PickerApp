import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import Team
from app.enums.user import UserRole

from tests.types import (
    BaseObjectFixtureCallable,
    BaseUserFixtureCallable, 
    BaseCreatorUsersFixtureCallable, 
    InputData, 
    RouteBaseFixture
)
from tests.constants import Roles, TEAMS_COUNT
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.test_lists import check_list_responces
from tests.utils.routes_utils import get_protected_routes
from tests.utils.common_fixtures import (
    test_base_user_from_role,
    test_base_creator_users_from_role,
    test_create_lobby_from_data,
    test_create_team_from_data,
    protected_route
)


all_routes = [
    ("POST",    "/api/v1/teams/",            Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/list-count",  Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/list",        Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/1",           Roles.ALL_ROLES),
    ("PUT",     "/api/v1/teams/1",           Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/teams/1",           Roles.ALL_ROLES),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_teams_routes_access(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole
):
    await check_access_for_authenticated_users(client_async, protected_route, test_base_user_from_role, role)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
async def test_teams_routes_require_auth(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
):
    await check_access_for_unauthenticated_users(client_async, protected_route)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "team_data, expected_status_team, error_substr_team",
    [
        ({"name":   "New Team"},    200,    ""),
        ({"name":   "   "},         422,    "name cannot be empty"),
        ({},                        422,    "Field required"),
    ]
)
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status_access, error_substr_access",
    [
        (UserRole.ADMIN,        False,  200,    ""),
        (UserRole.MODERATOR,    False,  200,    ""),
        (UserRole.USER,         True,   200,    ""),
        (UserRole.USER,         False,  403,    "No access to control team"),
    ]
)
@pytest.mark.parametrize(
    "lobby_exists, expected_status_lobby, error_substr_lobby",
    [
        (True,  200,    ""),
        (False, 404,    "Lobby not found"),
    ]
)
async def test_create_team(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        team_data: InputData,
        expected_status_team: int,
        error_substr_team: str,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status_access: int,
        error_substr_access: str,
        lobby_exists: bool,
        expected_status_lobby: int,
        error_substr_lobby: str
):

    route = "/api/v1/teams/"
    
    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    lobby_id, _ = await test_create_lobby_from_data(user if is_lobby_owner else creator, lobby_exists)
    team_data["lobby_id"] = lobby_id

    response: Response = await client_async.post(route, json=team_data, headers=headers)
    json_data = response.json()

    if expected_status_team != 200:
        assert response.status_code == expected_status_team, f"Expected {expected_status_team}, got {response.status_code}"
        assert error_substr_team in json_data["detail"][0]["msg"], f"Validation error mismatch: {json_data['detail'][0]['msg']}"
        return

    if expected_status_lobby != 200:
        assert response.status_code == expected_status_lobby, f"Expected {expected_status_lobby}, got {response.status_code}"
        assert error_substr_lobby in json_data["detail"], f"Expected error message '{error_substr_lobby}', got: {json_data['detail']}"
        return

    assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
    if expected_status_access != 200:
        assert error_substr_access in json_data["detail"], f"Expected error message '{error_substr_access}', got: {json_data['detail']}"
        return

    assert json_data["name"] == team_data["name"], "Team name does not match"
    assert json_data["lobby"]["id"] == team_data["lobby_id"], "Lobby ID does not match"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize(
    "team_exists, expected_status, error_substr",
    [
        (True,  200,    ""),
        (False, 404,    "Team not found"),
    ]
)
async def test_get_team_info(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        test_create_team_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        team_exists: bool,
        expected_status: int,
        error_substr: str
):
    
    user, headers = await test_base_user_from_role(role)
    _, lobby = await test_create_lobby_from_data(user)
    team_id, team = await test_create_team_from_data(lobby, team_exists)

    route = f"/api/v1/teams/{team_id}"
    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if not team_exists:
        assert error_substr in json_data["detail"], f"Expected error message '{error_substr}', got: {json_data['detail']}"
        return

    assert json_data["id"] == team.id, "Team ID does not match"
    assert json_data["name"] == team.name, "Team name does not match"
    assert json_data["lobby"]["id"] == lobby.id, "Lobby ID associated with team is incorrect"


# TODO: Update, because now I have `404` when data is empty
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_status, error_substr",
    [
        ({"name":   "Updated Team Name"},   200,    ""),
        ({"name":   "  "},                  422,    "Team name cannot be empty"),
        # ({},                                422,    "Field required"),
    ]
)
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status_access, error_substr_access",
    [
        (UserRole.ADMIN,        False,  200,    ""),
        (UserRole.MODERATOR,    False,  200,    ""),
        (UserRole.USER,         True,   200,    ""),
        (UserRole.USER,         False,  403,    "No access to control team"),
    ]
)
@pytest.mark.parametrize(
    "team_exists, expected_status_exists, error_substr_exists",
    [
        (True,  200,    ""),
        (False, 404,    "Team not found"),
    ]
)
async def test_update_team(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        test_create_team_from_data: BaseObjectFixtureCallable,
        update_data: InputData,
        role: UserRole,
        is_lobby_owner: bool,
        team_exists: bool,
        expected_status: int,
        expected_status_access: int,
        expected_status_exists: int,
        error_substr: str,
        error_substr_access: str,
        error_substr_exists: str,
):


    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    _, lobby = await test_create_lobby_from_data(user if is_lobby_owner else creator)
    team_id, _ = await test_create_team_from_data(lobby, team_exists)

    route = f"/api/v1/teams/{team_id}"
    response: Response = await client_async.put(route, json=update_data, headers=headers)
    
    json_data = response.json()
    if expected_status != 200:
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        assert error_substr in str(json_data["detail"]), f"Expected validation error message '{error_substr}', got: {json_data['detail']}"
        return

    if not team_exists:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_substr_exists in json_data["detail"], f"Expected error message '{error_substr_exists}', got: {json_data['detail']}"
        return

    assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
    if expected_status_access != 200:
        assert error_substr_access in str(json_data["detail"]), f"Expected error '{error_substr_access}', got: {json_data['detail']}"
        return

    assert json_data["name"] == update_data["name"], "Team name was not updated"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status_access, error_substr_access",
    [
        (UserRole.ADMIN,        False,  200,    ""),
        (UserRole.MODERATOR,    False,  200,    ""),
        (UserRole.USER,         True,   200,    ""),
        (UserRole.USER,         False,  403,    "No access to control team"),
    ]
)
@pytest.mark.parametrize(
    "team_exists, expected_status_exists, error_substr_exists",
    [
        (True,  200,    ""),
        (False, 404,    "Team not found"),
    ]
)
async def test_delete_team(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        test_create_team_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        is_lobby_owner: bool,
        team_exists: bool,
        expected_status_access: int,
        expected_status_exists: int,
        error_substr_access: str,
        error_substr_exists: str,
):

    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    _, lobby = await test_create_lobby_from_data(user if is_lobby_owner else creator)
    team_id, team = await test_create_team_from_data(lobby, team_exists)

    route = f"/api/v1/teams/{team_id}"
    response: Response = await client_async.delete(route, headers=headers)

    json_data = response.json()
    if expected_status_exists != 200:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_substr_exists in json_data["detail"], f"Expected error message '{error_substr_exists}', got: {json_data['detail']}"
        return

    assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
    if expected_status_access != 200:
        assert error_substr_access in json_data["detail"], f"Expected error message '{error_substr_access}', got: {json_data['detail']}"
        return

    # assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert json_data["description"] == f"Team '{team.name}' deleted successfully"


filter_data = [
    (None,                          TEAMS_COUNT),
    ({"id":         1},             1),
    ({"name":       "2"},           1),
    ({"name":       "Test Team"},   TEAMS_COUNT),
    ({"lobby_id":   1},             TEAMS_COUNT),
    ({"sort_by":    "id"},          TEAMS_COUNT),
    ({"sort_order": "desc"},        TEAMS_COUNT),
    ({"limit":      2},             2),
    ({"offset":     1},             TEAMS_COUNT-1),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data)
async def test_get_teams_list_with_filters(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        create_test_teams: list[Team],
        role: UserRole,
        filter_params: InputData,
        expected_count: int
):
    
    route = "/api/v1/teams/list"
    await check_list_responces(
        client_async, test_base_user_from_role, role, route, 
        expected_count=expected_count,
        is_total_count=False, 
        filter_params=filter_params,
        obj_type="teams"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data)
async def test_get_teams_list_count_with_filters(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        create_test_teams: list[Team],
        role: UserRole,
        filter_params: InputData,
        expected_count: int
):
    
    route = "/api/v1/teams/list-count"
    await check_list_responces(
        client_async, test_base_user_from_role, role, route, 
        expected_count=expected_count,
        is_total_count=True, 
        filter_params=filter_params,
        obj_type="teams"
    )
