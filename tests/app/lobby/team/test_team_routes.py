import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import Team, Algorithm
from app.enums.user import UserRole

from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory
from tests.factories.lobby_factory import LobbyFactory
from tests.factories.team_factory import TeamFactory

from tests.constants import Roles, TEAMS_COUNT
from tests.utils.user_utils import create_user_with_tokens
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.test_lists import check_list_responces
from tests.utils.routes_utils import get_protected_routes


all_routes = [
    ("POST",    "/api/v1/teams/",            Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/list-count",  Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/list",        Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/1",           Roles.ALL_ROLES),
    ("PUT",     "/api/v1/teams/1",           Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/teams/1",           Roles.ALL_ROLES),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("method, url, allowed_roles", get_protected_routes(all_routes))
async def test_teams_routes_access(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        role: UserRole,
        method: str,
        url: str,
        allowed_roles: tuple[UserRole, ...]
):
    await check_access_for_authenticated_users(client_async, user_factory, token_factory, role, method, url, allowed_roles)


@pytest.mark.asyncio
@pytest.mark.parametrize("method, url, allowed_roles", get_protected_routes(all_routes))
async def test_teams_routes_require_auth(
        client_async: AsyncClient, 
        method: str, 
        url: str, 
        allowed_roles: tuple[UserRole, ...]
):
    await check_access_for_unauthenticated_users(client_async, method, url)


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
        user_factory: UserFactory,
        token_factory: TokenFactory,
        test_algorithm: Algorithm,
        lobby_factory: LobbyFactory,
        team_data: dict[str, str],
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
    
    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    creator, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    if not lobby_exists:
        team_data["lobby_id"] = -1 
    else:
        if is_lobby_owner:
            lobby = await lobby_factory.create(user, test_algorithm)
        else:
            lobby = await lobby_factory.create(creator, test_algorithm)

        team_data["lobby_id"] = lobby.id

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
    "team_exists, expected_status, error_msg",
    [
        (True,  200, ""),
        (False, 404, "Team not found"),
    ]
)
async def test_get_team_info(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        test_team_id: int,
        role: UserRole,
        team_exists: bool,
        expected_status: int,
        error_msg: str
):

    team_id = test_team_id if team_exists else -1
    route = f"/api/v1/teams/{team_id}"

    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.get(route, headers=headers)
    json_data = response.json()

    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    if not team_exists:
        assert error_msg in json_data["detail"], f"Expected error message '{error_msg}', got: {json_data['detail']}"
        return 
    
    assert json_data["id"] == test_team_id, "Team ID does not match"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_status, error_msg",
    [
        ({"name":   "Updated Team Name"},   200,    ""),
        ({"name":   "  "},                  422,    "name cannot be empty"),
    ]
)
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status_access",
    [
        (UserRole.ADMIN,        False,  200),
        (UserRole.MODERATOR,    False,  200),
        (UserRole.USER,         True,   200),
        (UserRole.USER,         False,  403),
    ]
)
@pytest.mark.parametrize(
    "team_exists, expected_status_exists, error_msg_exists",
    [
        (True,  200,    ""),
        (False, 404,    "Team not found"),
    ]
)
async def test_update_team(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        lobby_factory: LobbyFactory,
        team_factory: TeamFactory,
        test_algorithm: Algorithm,
        update_data: dict[str, str],
        role: UserRole,
        is_lobby_owner: bool,
        team_exists: bool,
        expected_status: int,
        expected_status_access: int,
        expected_status_exists: int,
        error_msg: str,
        error_msg_exists: str,
):

    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    creator, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    if is_lobby_owner:
        lobby = await lobby_factory.create(user, test_algorithm)
    else:
        lobby = await lobby_factory.create(creator, test_algorithm)

    team_id = -1
    if team_exists:
        team = await team_factory.create(lobby)
        team_id = team.id

    route = f"/api/v1/teams/{team_id}"

    response: Response = await client_async.put(route, json=update_data, headers=headers)
    if expected_status != 200:
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        assert error_msg in response.json()["detail"][0]["msg"], f"Expected validation error message '{error_msg}', got: {response.json()['detail'][0]['msg']}"
        return

    if expected_status_exists != 200:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_msg_exists in response.json()["detail"], f"Expected error message '{error_msg_exists}', got: {response.json()['detail']}"
        return

    assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
    if expected_status_access != 200:
        return

    json_data = response.json()
    assert json_data["name"] == update_data["name"], "Team name was not updated"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status_access",
    [
        (UserRole.ADMIN,        False,  200),
        (UserRole.MODERATOR,    False,  200),
        (UserRole.USER,         True,   200),
        (UserRole.USER,         False,  403),
    ]
)
@pytest.mark.parametrize(
    "team_exists, expected_status_exists, error_msg_exists",
    [
        (True,  200,    ""),
        (False, 404,    "Team not found"),
    ]
)
async def test_delete_team(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        lobby_factory: LobbyFactory,
        team_factory: TeamFactory,
        test_algorithm: Algorithm,
        role: UserRole,
        is_lobby_owner: bool,
        team_exists: bool,
        expected_status_access: int,
        expected_status_exists: int,
        error_msg_exists: str,
):

    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    creator, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    if is_lobby_owner:
        lobby = await lobby_factory.create(user, test_algorithm)
    else:
        lobby = await lobby_factory.create(creator, test_algorithm)

    team_id = -1
    if team_exists:
        team = await team_factory.create(lobby)
        team_id = team.id

    route = f"/api/v1/teams/{team_id}"
    
    response: Response = await client_async.delete(route, headers=headers)
    if expected_status_exists != 200:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_msg_exists in response.json()["detail"], f"Expected error message '{error_msg_exists}', got: {response.json()['detail']}"
        return

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        return

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    json_data = response.json()
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
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_teams: list[Team],
        role: UserRole,
        filter_params: dict[str, str | int],
        expected_count: int
):
    
    route = "/api/v1/teams/list"
    await check_list_responces(
        client_async, user_factory, token_factory, role, route, 
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
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_teams: list[Team],
        role: UserRole,
        filter_params: dict[str, str | int],
        expected_count: int
):
    
    route = "/api/v1/teams/list-count"
    await check_list_responces(
        client_async, user_factory, token_factory, role, route, 
        expected_count=expected_count,
        is_total_count=True, 
        filter_params=filter_params,
        obj_type="teams"
    )
