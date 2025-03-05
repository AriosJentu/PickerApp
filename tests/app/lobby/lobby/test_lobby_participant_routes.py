import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import LobbyParticipant
from app.enums.user import UserRole
from app.enums.lobby import LobbyParticipantRole

from tests.types import (
    BaseObjectFixtureCallable,
    BaseUserFixtureCallable,
    BaseCreatorUsersFixtureCallable,
    BaseCreatorAdditionalUsersFixtureCallable,
    InputData,
    RouteBaseFixture
)
from tests.constants import Roles, PARTICIPANTS_COUNT
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.test_lists import check_list_responces
from tests.utils.routes_utils import get_protected_routes
from tests.utils.common_fixtures import (
    test_base_user_from_role,
    test_base_creator_users_from_role,
    test_base_creator_additional_users_from_role,
    test_create_lobby_from_data,
    test_create_team_from_data,
    protected_route
)


all_routes = [
    ("GET",     "/api/v1/lobby/1/participants-count",   Roles.ALL_ROLES),
    ("GET",     "/api/v1/lobby/1/participants",         Roles.ALL_ROLES),
    ("POST",    "/api/v1/lobby/1/participants",         Roles.ALL_ROLES),
    ("PUT",     "/api/v1/lobby/1/participants/1",       Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/lobby/1/participants/1",       Roles.ALL_ROLES),
    ("POST",    "/api/v1/lobby/1/connect",              Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/lobby/1/leave",                Roles.ALL_ROLES),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_lobby_participants_routes_access(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole
):
    await check_access_for_authenticated_users(client_async, protected_route, test_base_user_from_role, role)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
async def test_lobby_participants_routes_require_auth(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
):
    await check_access_for_unauthenticated_users(client_async, protected_route)


@pytest.mark.asyncio
@pytest.mark.parametrize("with_team", [True, False])
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status",
    [
        (UserRole.ADMIN,        False,  200),
        (UserRole.MODERATOR,    False,  200),
        (UserRole.USER,         True,   200),
        (UserRole.USER,         False,  403),
    ]
)
async def test_add_participant(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        test_create_team_from_data: BaseObjectFixtureCallable,
        with_team: bool,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status: int,
):

    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    lobby_id, lobby = await test_create_lobby_from_data(user if is_lobby_owner else creator)
    team_id, _ = await test_create_team_from_data(lobby)

    route = f"/api/v1/lobby/{lobby_id}/participants"

    params = {"user_id": user.id}
    if with_team:
        params["team_id"] = team_id

    response: Response = await client_async.post(route, params=params, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status == 200:
        json_data = response.json()
        assert json_data["lobby"]["id"] == lobby_id, f"Lobby ID is not the same as participant added to"
        assert json_data["user"]["id"] == user.id, f"User ID is not the same as participant's"
        assert json_data["role"] == LobbyParticipantRole.SPECTATOR, f"Participant has incorrect role"

        if with_team:
            assert json_data["team"]["id"] == team_id, f"Team ID is not the same as participant added to"


@pytest.mark.asyncio
@pytest.mark.parametrize("update_data", [
    {"role":        LobbyParticipantRole.PLAYER}, 
    {"team_id":     None},
    {"is_active":   False},
])
@pytest.mark.parametrize(
    "role, is_lobby_owner, expected_status",
    [
        (UserRole.ADMIN,        False,  200),
        (UserRole.MODERATOR,    False,  200),
        (UserRole.USER,         True,   200),
        (UserRole.USER,         False,  403),
    ]
)
async def test_edit_participant(
        client_async: AsyncClient,
        test_base_creator_additional_users_from_role: BaseCreatorAdditionalUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        test_create_team_from_data: BaseObjectFixtureCallable,
        update_data: InputData,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status: int
):

    user, headers, creator, headers_creator, user_to_add, _ = await test_base_creator_additional_users_from_role(role)
    lobby_id, lobby = await test_create_lobby_from_data(user if is_lobby_owner else creator)
    team_id, _ = await test_create_team_from_data(lobby)

    route_add = f"/api/v1/lobby/{lobby_id}/participants"
    params = {"user_id": user_to_add.id, "team_id": team_id}
    
    response: Response = await client_async.post(route_add, params=params, headers=(headers if is_lobby_owner else headers_creator))
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["user"]["id"] == user_to_add.id, f"Expected User ID {user_to_add.id}, got {json_data["user"]["id"]}"
    participant_id = json_data["id"]

    route = f"/api/v1/lobby/{lobby_id}/participants/{participant_id}"
    response: Response = await client_async.put(route, json=update_data, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status == 200:
        json_data = response.json()
        assert json_data["lobby"]["id"] == lobby_id, f"Lobby ID is not the same as participant added to"
        assert json_data["user"]["id"] == user_to_add.id, f"User ID is not the same as participant's"

        if "role" in update_data:
            assert json_data["role"] == update_data["role"], f"Role was not updated"

        if "team_id" in update_data and update_data["team_id"] is not None:
            assert json_data["team"]["id"] == update_data["team_id"], f"Team ID was not updated"

        if "team_id" in update_data and update_data["team_id"] is None:
            assert json_data["team"] == update_data["team_id"], f"Team was not nulled"

        if "is_active" in update_data:
            assert json_data["is_active"] == update_data["is_active"], f"Active state was not updated"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_connect_to_lobby(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        test_lobby_id: int,
        role: UserRole
):

    route = f"/api/v1/lobby/{test_lobby_id}/connect"
    user, headers = await test_base_user_from_role(role)

    response: Response = await client_async.post(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["lobby"]["id"] == test_lobby_id, f"Expected Lobby ID {test_lobby_id}, got {json_data["lobby"]["id"]}"
    assert json_data["user"]["id"] == user.id, f"Expected User ID {user.id}, got {json_data["user"]["id"]}"

    
    response: Response = await client_async.post(route, headers=headers)
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    
    json_data = response.json()
    assert json_data["detail"] == "User already in lobby", f"Expected that user already in lobby"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_leave_lobby(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        test_lobby_id: int,
        role: UserRole
):

    route = f"/api/v1/lobby/{test_lobby_id}/leave"
    route_connect = f"/api/v1/lobby/{test_lobby_id}/connect"
    user, headers = await test_base_user_from_role(role)

    await client_async.post(route_connect, headers=headers)
    
    response: Response = await client_async.delete(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["lobby"]["id"] == test_lobby_id, f"Expected Lobby ID {test_lobby_id}, got {json_data["lobby"]["id"]}"
    assert json_data["user"]["id"] == user.id, f"Expected User ID {user.id}, got {json_data["user"]["id"]}"


    response: Response = await client_async.delete(route, headers=headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    json_data = response.json()
    assert json_data["detail"] == "Participant not found", f"Expected that participant already not in lobby"


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
async def test_kick_from_lobby(
        client_async: AsyncClient,
        test_base_creator_additional_users_from_role: BaseCreatorAdditionalUsersFixtureCallable,
        test_create_lobby_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status: int
):

    user, headers, creator, headers_creator, user_to_add, _ = await test_base_creator_additional_users_from_role(role)
    lobby_id, _ = await test_create_lobby_from_data(user if is_lobby_owner else creator)

    route_add = f"/api/v1/lobby/{lobby_id}/participants"
    params = {"user_id": user_to_add.id}
    
    response: Response = await client_async.post(route_add, params=params, headers=(headers if is_lobby_owner else headers_creator))
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["user"]["id"] == user_to_add.id, f"Expected User ID {user_to_add.id}, got {json_data["user"]["id"]}"
    participant_id = json_data["id"]

    route = f"/api/v1/lobby/{lobby_id}/participants/{participant_id}"
    response: Response = await client_async.delete(route, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status == 200:
        response: Response = await client_async.delete(route, headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

        json_data = response.json()
        assert json_data["detail"] == "Participant not found", f"Expected that participant already not in lobby"


filter_data = [
    (None,                                                  PARTICIPANTS_COUNT),
    ({"id":         1},                                     1),
    ({"user_id":    3},                                     1),
    ({"team_id":    1},                                     0),
    ({"role":       LobbyParticipantRole.SPECTATOR.value},  PARTICIPANTS_COUNT),
    ({"sort_by":    "id"},                                  PARTICIPANTS_COUNT),
    ({"sort_order": "desc"},                                PARTICIPANTS_COUNT),
    ({"limit":      2},                                     2),
    ({"offset":     1},                                     PARTICIPANTS_COUNT-1),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data)
async def test_get_lobby_participants_with_filters(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        test_lobby_id: int,
        create_test_participants: list[LobbyParticipant],
        role: UserRole,
        filter_params: InputData,
        expected_count: int
):
    
    route = f"/api/v1/lobby/{test_lobby_id}/participants"
    await check_list_responces(
        client_async, test_base_user_from_role, role, route, 
        expected_count=expected_count,
        is_total_count=False, 
        filter_params=filter_params,
        obj_type="participants"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data)
async def test_get_lobby_participants_count_with_filters(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        test_lobby_id: int,
        create_test_participants: list[LobbyParticipant],
        role: UserRole,
        filter_params: InputData,
        expected_count: int
):
    
    route = f"/api/v1/lobby/{test_lobby_id}/participants-count"
    await check_list_responces(
        client_async, test_base_user_from_role, role, route, 
        expected_count=expected_count,
        is_total_count=True, 
        filter_params=filter_params,
        obj_type="participants"
    )
