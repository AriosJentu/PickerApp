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
from tests.utils.test_lists import check_list_responces
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
            {"name": "Valid Algorithm", "algorithm": "BB PP T", "teams_count": 2},
            200, ""
        ),
        (
            {"name": "Invalid Step", "algorithm": "MM FS P", "teams_count": 2},
            422, "Step 'MM' containings incorrect symbols"
        ),
        (
            {"name": "Wrong Step Size", "algorithm": "BBB PPP T", "teams_count": 2},
            422, "Size of the step 'BBB' must be equal to teams count"
        ),
        (
            {"name": "  ", "algorithm": "BB PP T", "teams_count": 2},
            422, "Algorithm name cannot be empty"
        ),
        (
            {"name": "Missing Algorithm", "algorithm": "", "teams_count": 2},
            422, "Algorithm should contain at least one step"
        ),
        (
            {"name": "Negative Teams Count", "algorithm": "BB PP T", "teams_count": -1},
            422, "Teams count should be in between 2 and 16"
        ),
        (
            {}, 
            422, "Field required"
        ),
        (
            {"name": "No Algorithm"}, 
            422, "Field required"
        ),
        (
            {"algorithm": "BB PP T"}, 
            422, "Field required"
        ),
        (
            {"name": "No Teams Count", "algorithm": "BB PP T"}, 
            422, "Field required"
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
        role: UserRole,
):

    route = "/api/v1/algorithm/"
    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    headers = {"Authorization": f"Bearer {access_token}"}

    algorithm_data["creator_id"] = user.id
    response: Response = await client_async.post(route, json=algorithm_data, headers=headers)

    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    if expected_status != 200:
        assert error_substr in response.json()["detail"][0]["msg"], f"Incorrect validation response: {response.json()['detail'][0]['msg']}"
        return

    json_data = response.json()
    assert json_data["name"] == algorithm_data["name"], "Algorithm name does not match"
    assert json_data["algorithm"] == algorithm_data["algorithm"], "Algorithm script does not match"
    assert json_data["teams_count"] == algorithm_data["teams_count"], "Teams count does not match"
    assert json_data["creator"]["id"] == user.id, "Algorithm creator does not match"


#TODO: Test Get Algorithm Info


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_status, error_substr",
    [
        (
            {"name": "Valid Algorithm", "algorithm": "BB PP T", "teams_count": 2},
            200, ""
        ),
        (
            {"name": "Invalid Step", "algorithm": "MM FS P", "teams_count": 2},
            422, "Step 'MM' containings incorrect symbols"
        ),
        (
            {"name": "Wrong Step Size", "algorithm": "BBB PPP T", "teams_count": 2},
            422, "Size of the step 'BBB' must be equal to teams count"
        ),
        (
            {"name": "  ", "algorithm": "BB PP T", "teams_count": 2},
            422, "Algorithm name cannot be empty"
        ),
        (
            {"name": "Missing Algorithm", "algorithm": "", "teams_count": 2},
            422, "Algorithm should contain at least one step"
        ),
        (
            {"name": "Negative Teams Count", "algorithm": "BB PP T", "teams_count": -1},
            422, "Teams count should be in between 2 and 16"
        ),
        (
            {}, 
            422, "Field required"
        ),
        (
            {"name": "No Algorithm"}, 
            422, "Field required"
        ),
        (
            {"algorithm": "BB PP T"}, 
            422, "Field required"
        ),
        (
            {"name": "No Teams Count", "algorithm": "BB PP T"}, 
            422, "Field required"
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
@pytest.mark.parametrize(
    "algorithm_exists, expected_status_exists, error_msg_exists",
    [
        (True,  200,    ""),
        (False, 404,    "Algorithm not found"),
    ]
)
async def test_update_algorithm(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        algorithm_factory: AlgorithmFactory,
        role: UserRole,
        is_creator: bool,
        algorithm_exists: bool,
        expected_status_access: int,
        expected_status_exists: int,
        update_data: dict[str, str | int],
        expected_status: int,
        error_substr: str,
        error_msg_exists: str
):
    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    creator, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    algorithm_id = -1
    if algorithm_exists:
        algorithm = await algorithm_factory.create(user if is_creator else creator)
        algorithm_id = algorithm.id

    route = f"/api/v1/algorithm/{algorithm_id}"
    response: Response = await client_async.put(route, json=update_data, headers=headers)

    if expected_status != 200:
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        message = response.json()["detail"][0]["msg"]
        assert error_substr in message, f"Expected validation error '{error_substr}', got: {message}"
        return
    
    if not algorithm_exists:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_msg_exists in response.json()["detail"], f"Expected error message '{error_msg_exists}', got: {response.json()["detail"]}"
        return

    assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
    if expected_status_access != 200:
        return
    
    json_data = response.json()
    assert json_data["name"] == update_data["name"], "Algorithm name was not updated"
    assert json_data["algorithm"] == update_data["algorithm"], "Algorithm script was not updated"
    assert json_data["teams_count"] == update_data["teams_count"], "Teams count was not updated"    


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role, is_creator, expected_status_access",
    [
        (UserRole.ADMIN,        False,  200),
        (UserRole.MODERATOR,    False,  200),
        (UserRole.USER,         True,   200),
        (UserRole.USER,         False,  403),
    ]
)
@pytest.mark.parametrize(
    "algorithm_exists, expected_status_exists, error_msg_exists",
    [
        (True,  200,    ""),
        (False, 404,    "Algorithm not found"),
    ]
)
async def test_delete_algorithm(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        algorithm_factory: AlgorithmFactory,
        role: UserRole,
        is_creator: bool,
        algorithm_exists: bool,
        expected_status_access: int,
        expected_status_exists: int,
        error_msg_exists: str,
):

    user, access_token, _ = await create_user_with_tokens(user_factory, token_factory, role)
    creator, _, _ = await create_user_with_tokens(user_factory, token_factory, prefix="creator_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    algorithm_id = -1
    if algorithm_exists:
        algorithm = await algorithm_factory.create(user if is_creator else creator)
        algorithm_id = algorithm.id

    route = f"/api/v1/algorithm/{algorithm_id}"
    response: Response = await client_async.delete(route, headers=headers)

    if not algorithm_exists:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_msg_exists in response.json().get("detail", ""), f"Expected error message '{error_msg_exists}', got: {response.json().get('detail', '')}"
        return

    assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
    if expected_status_access != 200:
        return

    json_data = response.json()
    assert json_data["id"] == algorithm_id, "Algorithm ID is not correct"
    assert algorithm.name in json_data["description"], "Algorithm name is not in response description"


filter_data = [
    (None,                                  ALGORITHMS_COUNT),
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

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data)
async def test_get_algorithms_list_with_filters(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_algorithms: list[Algorithm],
        role: UserRole,
        filter_params: dict[str, str | int],
        expected_count: int
):
    
    route = "/api/v1/algorithm/list"
    await check_list_responces(
        client_async, user_factory, token_factory, role, route, 
        expected_count=expected_count,
        is_total_count=False, 
        filter_params=filter_params,
        obj_type="algorithms"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data)
async def test_get_algorithms_list_count_with_filters(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_algorithms: list[Algorithm],
        role: UserRole,
        filter_params: dict[str, str | int],
        expected_count: int
):
    
    route = "/api/v1/algorithm/list-count"
    await check_list_responces(
        client_async, user_factory, token_factory, role, route, 
        expected_count=expected_count,
        is_total_count=True, 
        filter_params=filter_params,
        obj_type="algorithms"
    )
