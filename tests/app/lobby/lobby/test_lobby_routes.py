import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import Lobby, Algorithm 
from app.enums.user import UserRole
from app.enums.lobby import LobbyStatus

from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory
from tests.factories.lobby_factory import LobbyFactory

from tests.constants import Roles, LOBBIES_COUNT
from tests.utils.user_utils import create_user_with_tokens
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.routes_utils import get_protected_routes


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
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("method, url, allowed_roles", get_protected_routes(all_routes))
async def test_account_routes_access(
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
async def test_account_routes_require_auth(
        client_async: AsyncClient,
        method: str, 
        url: str, 
        allowed_roles: tuple[UserRole, ...]
):
    await check_access_for_unauthenticated_users(client_async, method, url)


@pytest.mark.asyncio
@pytest.mark.parametrize("lobby_data", [{"name": "New Lobby"}])
@pytest.mark.parametrize("role", Roles.LIST)
async def test_create_lobby(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        test_algorithm_id: int,
        lobby_data: dict[str, str],
        role: UserRole
):

    route = "/api/v1/lobby/"
    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}
    
    lobby_data["host_id"] = user.id
    lobby_data["algorithm_id"] = test_algorithm_id

    response: Response = await client_async.post(route, json=lobby_data, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["name"] == lobby_data["name"], "Lobby name does not match"


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
        user_factory: UserFactory,
        token_factory: TokenFactory,
        lobby_factory: LobbyFactory,
        test_algorithm: Algorithm,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status: int,
        update_data: dict[str, str]
):

    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role=role)
    creator, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    if is_lobby_owner:
        lobby = await lobby_factory.create(user, test_algorithm)
    else:
        lobby = await lobby_factory.create(creator, test_algorithm)
    
    route = f"/api/v1/lobby/{lobby.id}"

    response: Response = await client_async.put(route, json=update_data, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status == 200:
        json_data = response.json()
        assert json_data["name"] == update_data["name"], "Lobby name was not updated"
        assert json_data["status"] == LobbyStatus.ACTIVE, f"Lobby status isn't Active, got {json_data["status"]}"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_lobbies_list(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_lobbies: list[Lobby],
        role: UserRole
):

    route = "/api/v1/lobby/list"
    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert len(json_data) == LOBBIES_COUNT, f"Expected {LOBBIES_COUNT}, got {len(json_data)}"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_lobbies_list_count(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_lobbies: list[Lobby],
        role: UserRole
):
    
    route = "/api/v1/lobby/list-count"
    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    json_data = response.json()
    assert json_data["total_count"] == LOBBIES_COUNT, f"Expected {LOBBIES_COUNT}, got {len(json_data)}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filter_params, expected_count",
    [
        ({"id":             1},             1),
        ({"name":           "2"},           1),
        ({"name":           "Test Lobby"},  LOBBIES_COUNT),
        ({"host_id":        "0"},           LOBBIES_COUNT),
        ({"host_id":        "1"},           0),
        ({"algorithm_id":   "1"},           LOBBIES_COUNT),
        ({"sort_by":        "id"},          LOBBIES_COUNT),
        ({"sort_order":     "desc"},        LOBBIES_COUNT),
        ({"limit":          2},             2),
        ({"offset":         1},             LOBBIES_COUNT-1),
    ]
)
async def test_get_lobbies_list_with_filters(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_lobbies: list[Lobby],
        filter_params: dict[str, str | int],
        expected_count: int
):
    
    route = "/api/v1/lobby/list"
    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.get(route, headers=headers, params=filter_params)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    error_msg = f"Expected {expected_count} teams for filter `{filter_params}`, got {len(json_data)}"
    assert len(json_data) == expected_count, error_msg


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
        user_factory: UserFactory,
        token_factory: TokenFactory,
        lobby_factory: LobbyFactory,
        test_algorithm: Algorithm,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status: int,
):

    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role=role)
    creator, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    if is_lobby_owner:
        lobby = await lobby_factory.create(user, test_algorithm)
    else:
        lobby = await lobby_factory.create(creator, test_algorithm)
    
    route = f"/api/v1/lobby/{lobby.id}/close"

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
        user_factory: UserFactory,
        token_factory: TokenFactory,
        lobby_factory: LobbyFactory,
        test_algorithm: Algorithm,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status: int,
):

    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role=role)
    creator, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    if is_lobby_owner:
        lobby = await lobby_factory.create(user, test_algorithm)
    else:
        lobby = await lobby_factory.create(creator, test_algorithm)
    
    route = f"/api/v1/lobby/{lobby.id}"

    response: Response = await client_async.delete(route, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status == 200:
        json_data = response.json()
        assert json_data["id"] == lobby.id, f"Expected {lobby.id}, got {json_data["id"]}"
        assert lobby.name in json_data["description"], f"Deleted lobby with incorrect name"
