import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import Team, Algorithm
from app.enums.user import UserRole

from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory
from tests.factories.lobby_factory import LobbyFactory
from tests.factories.team_factory import TeamFactory

from tests.utils.user_utils import create_user_with_tokens, Roles
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.routes_utils import get_protected_routes


all_routes = [
    ("POST",    "/api/v1/teams/",            Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/list-count",  Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/list",        Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/1",           None),
    ("PUT",     "/api/v1/teams/1",           None),
    ("DELETE",  "/api/v1/teams/1",           None),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("method, url, allowed_roles", get_protected_routes(all_routes))
async def test_team_routes_access(
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
async def test_team_routes_require_auth(
        client_async: AsyncClient, 
        method: str, 
        url: str, 
        allowed_roles: tuple[UserRole, ...]
):
    await check_access_for_unauthenticated_users(client_async, method, url)


@pytest.mark.asyncio
@pytest.mark.parametrize("team_data", [{"name": "New Team"}])
@pytest.mark.parametrize("role", Roles.LIST)
async def test_create_team(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        test_algorithm: Algorithm,
        lobby_factory: LobbyFactory,
        team_data: dict[str, str],
        role: UserRole
):
    route = "/api/v1/teams/"
    owner, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}
    
    lobby = await lobby_factory.create(owner, test_algorithm)
    team_data["lobby_id"] = lobby.id

    response: Response = await client_async.post(route, json=team_data, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["name"] == team_data["name"], "Team name does not match"


@pytest.mark.asyncio
@pytest.mark.parametrize("team_data", [{"name": "Unauthorized Team"}])
@pytest.mark.parametrize("role, expected_status", [
    (UserRole.USER,         403),
    (UserRole.MODERATOR,    200),
    (UserRole.ADMIN,        200),
])
async def test_create_team_no_access(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        lobby_factory: LobbyFactory,
        test_algorithm: Algorithm,
        team_data: dict[str, str],
        role: UserRole,
        expected_status: int
):

    route = "/api/v1/teams/"
    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    creator, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    lobby = await lobby_factory.create(creator, test_algorithm)
    team_data["lobby_id"] = lobby.id

    response: Response = await client_async.post(route, json=team_data, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status == 200:
        json_data = response.json()
        assert json_data["name"] == team_data["name"]
        assert json_data["lobby"]["id"] == lobby.id

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_teams_list(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_teams: list[Team],
        role: UserRole
):
    
    route = "/api/v1/teams/list"
    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    json_data = response.json()
    assert len(json_data) == len(create_test_teams), f"Expected {len(create_test_teams)}, got {len(json_data)}"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_team_info(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        test_team_id: int,
        role: UserRole
):

    route = f"/api/v1/teams/{test_team_id}"
    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["id"] == test_team_id, "Team ID does not match"


@pytest.mark.asyncio
@pytest.mark.parametrize("update_data", [{"name": "Updated Team Name"}])
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status",
    [
        (UserRole.ADMIN,        False,  200),
        (UserRole.MODERATOR,    False,  200),
        (UserRole.USER,         True,   200),
        (UserRole.USER,         False,  403),
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
        expected_status: int
):
    
    owner, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    other_owner, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    if is_lobby_owner:
        lobby = await lobby_factory.create(owner, test_algorithm)
    else:
        lobby = await lobby_factory.create(other_owner, test_algorithm)

    team = await team_factory.create(lobby)
    route = f"/api/v1/teams/{team.id}"

    response: Response = await client_async.put(route, json=update_data, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status == 200:
        json_data = response.json()
        assert json_data["name"] == update_data["name"], "Team name was not updated"


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
async def test_delete_team_different_users(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        lobby_factory: LobbyFactory,
        team_factory: TeamFactory,
        test_algorithm: Algorithm,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status: int
):

    owner, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    other_owner, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    if is_lobby_owner:
        lobby = await lobby_factory.create(owner, test_algorithm)
    else:
        lobby = await lobby_factory.create(other_owner, test_algorithm)

    team = await team_factory.create(lobby)
    route = f"/api/v1/teams/{team.id}"

    response: Response = await client_async.delete(route, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status == 200:
        json_data = response.json()
        assert json_data["description"] == f"Team '{team.name}' deleted successfully"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_delete_team_not_found(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        role: UserRole
):
    
    route = f"/api/v1/teams/1"
    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.delete(route, headers=headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
