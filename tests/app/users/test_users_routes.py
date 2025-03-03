import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import User
from app.enums.user import UserRole

from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory

from tests.constants import Roles, USERS_COUNT
from tests.utils.user_utils import create_user_with_tokens
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.routes_utils import get_protected_routes


all_routes = [
    ("GET",     "/api/v1/users/list",       Roles.ALL_ROLES),
    ("GET",     "/api/v1/users/list-count", Roles.ALL_ROLES),
    ("GET",     "/api/v1/users/",           Roles.ALL_ROLES),
    ("PUT",     "/api/v1/users/",           Roles.ADMIN),
    ("DELETE",  "/api/v1/users/",           Roles.ADMIN),
    ("DELETE",  "/api/v1/users/tokens",     Roles.ADMIN),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("method, url, allowed_roles", get_protected_routes(all_routes))
async def test_users_routes_access(
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
async def test_users_routes_require_auth(
        client_async: AsyncClient, 
        method: str, 
        url: str, 
        allowed_roles: tuple[UserRole, ...]
):
    await check_access_for_unauthenticated_users(client_async, method, url)


@pytest.mark.asyncio
async def test_get_users_list(
        client_async: AsyncClient,
        create_multiple_test_users_with_tokens: list[tuple[User, str]]
):

    route = "/api/v1/users/list"
    users_list = create_multiple_test_users_with_tokens

    _, user_access_token = users_list[0]
    headers = {"Authorization": f"Bearer {user_access_token}"}

    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    json_data = response.json()
    error_msg = f"Expected {len(users_list)} users, got {len(json_data)}"
    assert len(json_data) == len(users_list), error_msg


@pytest.mark.asyncio
async def test_get_users_list_count(
        client_async: AsyncClient,
        create_multiple_test_users_with_tokens: list[tuple[User, str]]
):

    route = "/api/v1/users/list-count"
    users_list = create_multiple_test_users_with_tokens

    _, user_access_token = users_list[0]
    headers = {"Authorization": f"Bearer {user_access_token}"}

    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    json_data = response.json()
    error_msg = f"Expected {USERS_COUNT} users, got {len(json_data)}"
    assert json_data["total_count"] == USERS_COUNT, error_msg


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filter_params, expected_count",
    [
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
)
async def test_get_users_list_with_filters(
        client_async: AsyncClient,
        create_test_users: list[User],
        user_factory: UserFactory,
        token_factory: TokenFactory,
        filter_params: dict[str, str | int],
        expected_count: int
):
    
    route = "/api/v1/users/list"
    _, access_token, _ = await create_user_with_tokens(user_factory, token_factory)
    headers = {"Authorization": f"Bearer {access_token}"}

    response: Response = await client_async.get(route, headers=headers, params=filter_params)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    error_msg = f"Expected {expected_count} users for filter `{filter_params}`, got {len(json_data)}"
    assert len(json_data) == expected_count, error_msg
