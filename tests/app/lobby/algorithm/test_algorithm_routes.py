import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import Algorithm
from app.enums.user import UserRole

from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory
from tests.factories.algorithm_factory import AlgorithmFactory

from tests.constants import Roles, ALGORITHMS_COUNT
from tests.utils.user_utils import create_user_with_tokens
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.routes_utils import get_protected_routes


all_routes = [
    ("POST",    "/api/v1/algorithm/",            Roles.ALL_ROLES),
    ("GET",     "/api/v1/algorithm/list-count",  Roles.ALL_ROLES),
    ("GET",     "/api/v1/algorithm/list",        Roles.ALL_ROLES),
    ("GET",     "/api/v1/algorithm/1",           Roles.ALL_ROLES),
    ("PUT",     "/api/v1/algorithm/1",           Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/algorithm/1",           Roles.ALL_ROLES),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("method, url, allowed_roles", get_protected_routes(all_routes))
async def test_algorithm_routes_access(
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
async def test_algorithm_routes_require_auth(
        client_async: AsyncClient, 
        method: str, 
        url: str, 
        allowed_roles: tuple[UserRole, ...]
):
    await check_access_for_unauthenticated_users(client_async, method, url)


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize(
    "algorithm_data, expected_status, error_substr",
    [
        (
            {"name":    "New Algorithm",        "algorithm":    "BB PP T",      "teams_count":  2},
            200, ""
        ),
        (
            {"name":    "Invalid Algorithm",    "algorithm":    "MM FS P",      "teams_count":  2},
            422, "Step 'MM' containings incorrect symbols"
        ),
        (
            {"name":    "Wrong Step Size",      "algorithm":    "BBB PPP T",    "teams_count":  2},
            422, "Size of the step 'BBB' must be equal to teams count"
        ),
    ]
)
async def test_create_algorithm(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        algorithm_data: dict[str, str | int],
        expected_status: int,
        error_substr: str,
        role: UserRole
):

    route = "/api/v1/algorithm/"
    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}

    algorithm_data["creator_id"] = user.id

    response: Response = await client_async.post(route, json=algorithm_data, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if expected_status == 200:
        assert json_data["name"] == algorithm_data["name"], "Algorithm name does not match"
        assert json_data["algorithm"] == algorithm_data["algorithm"], "Algorithm script does not match"
        assert json_data["creator"]["id"] == user.id, "Algorithm creator does not match"
    else:
        assert error_substr in str(json_data["detail"]), f"Incorrect validation response: {json_data["detail"][0]["msg"]}"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_algorithm_info(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        test_algorithm: Algorithm,
        role: UserRole
):

    route = f"/api/v1/algorithm/{test_algorithm.id}"
    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
 
    json_data = response.json()
    assert json_data["id"] == test_algorithm.id, "Algorithm ID is not correct"
    assert json_data["name"] == test_algorithm.name, "Algorithm name is not correct"
    assert json_data["algorithm"] == test_algorithm.algorithm, "Algorithm script is not correct"
    assert json_data["teams_count"] == test_algorithm.teams_count, "Teams count is not correct"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_status, error_substr",
    [
        (
            {"name":    "Updated Algorithm",    "algorithm":    "BB PP T",      "teams_count":  2},
            200, ""
        ),
        (
            {"name":    "Invalid Algorithm",    "algorithm":    "MM FS P",      "teams_count":  2},
            422, "Step 'MM' containings incorrect symbols"
        ),
        (
            {"name":    "Wrong Step Size",      "algorithm":    "BBB PPP T",    "teams_count":  2},
            422, "Size of the step 'BBB' must be equal to teams count"
        ),
    ]
)
@pytest.mark.parametrize(
    "role, is_creator, expected_status_access",
    [
        (UserRole.ADMIN,        False,  200),
        (UserRole.MODERATOR,    False,  200),
        (UserRole.USER,         True,   200),
        (UserRole.USER,         False,  403),
    ]
)
async def test_update_algorithm(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        algorithm_factory: AlgorithmFactory,
        role: UserRole,
        is_creator: bool,
        expected_status_access: int,
        update_data: dict[str, str | int],
        expected_status: int,
        error_substr: str
):

    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    other_owner, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    if is_creator:
        algorithm = await algorithm_factory.create(user)
    else:
        algorithm = await algorithm_factory.create(other_owner)

    route = f"/api/v1/algorithm/{algorithm.id}"

    response: Response = await client_async.put(route, json=update_data, headers=headers)
    actual_status = response.status_code

    if expected_status_access == 403 and expected_status == 200:
        expected_status = expected_status_access

    assert actual_status == expected_status, f"Expected {expected_status}, got {actual_status}"

    json_data = response.json()
    if expected_status == 200:
        assert json_data["name"] == update_data["name"], "Algorithm name was not updated"
        assert json_data["algorithm"] == update_data["algorithm"], "Algorithm script was not updated"
        assert json_data["teams_count"] == update_data["teams_count"], "Teams count was not updated"
    else:
        assert error_substr in str(json_data["detail"]), f"Incorrect validation response: {json_data['detail'][0]['msg']}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role, is_creator, expected_status",
    [
        (UserRole.ADMIN,        False,  200),
        (UserRole.MODERATOR,    False,  200),
        (UserRole.USER,         True,   200),
        (UserRole.USER,         False,  403),
    ]
)
async def test_delete_algorithm(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        algorithm_factory: AlgorithmFactory,
        role: UserRole,
        is_creator: bool,
        expected_status: int,
):

    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    other_owner, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    if is_creator:
        algorithm = await algorithm_factory.create(user)
    else:
        algorithm = await algorithm_factory.create(other_owner)

    route = f"/api/v1/algorithm/{algorithm.id}"

    response: Response = await client_async.delete(route, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if expected_status == 200:
        assert json_data["id"] == algorithm.id, "Algorithm ID is not correct"
        assert algorithm.name in json_data["description"], "Algorithm name is not in response description"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_algorithms_list(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_algorithms: list[Algorithm],
        role: UserRole
):

    route = "/api/v1/algorithm/list"
    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
 
    json_data = response.json()
    assert len(json_data) == ALGORITHMS_COUNT, f"Expected {ALGORITHMS_COUNT}, got {len(json_data)}"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_algorithms_list_count(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_algorithms: list[Algorithm],
        role: UserRole
):

    route = "/api/v1/algorithm/list-count"
    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
 
    json_data = response.json()
    assert json_data["total_count"] == ALGORITHMS_COUNT, f"Expected {ALGORITHMS_COUNT}, got {len(json_data)}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filter_params, expected_count",
    [
        ({"id":             1},                 1),
        ({"name":           "2"},               1),
        ({"name":           "Test Algorithm"},  ALGORITHMS_COUNT),
        ({"teams_count":    2},                 ALGORITHMS_COUNT),
        ({"teams_count":    3},                 0),
        ({"sort_by":        "id"},              ALGORITHMS_COUNT),
        ({"sort_order":     "desc"},            ALGORITHMS_COUNT),
        ({"limit":          2},                 2),
        ({"offset":         1},                 ALGORITHMS_COUNT-1),
    ]
)
async def test_get_algorithms_list_with_filters(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_algorithms: list[Algorithm],
        filter_params: dict[str, str | int],
        expected_count: int
):
    
    route = "/api/v1/algorithm/list"
    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.get(route, headers=headers, params=filter_params)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    error_msg = f"Expected {expected_count} teams for filter `{filter_params}`, got {len(json_data)}"
    assert len(json_data) == expected_count, error_msg
