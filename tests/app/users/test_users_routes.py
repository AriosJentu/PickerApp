import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import User
from app.enums.user import UserRole

from tests.factories.user_factory import UserFactory
from tests.factories.token_factory import TokenFactory

from tests.constants import Roles, USERS_COUNT
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.test_lists import check_list_responces
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


filter_data_multiple = [
    (None,                                      USERS_COUNT+1),
    ({"id":         1},                         1),
    ({"username":   "testuser"},                USERS_COUNT+1),
    ({"sort_by":    "id"},                      USERS_COUNT+1),
    ({"sort_order": "desc"},                    USERS_COUNT+1),
    ({"limit":      2},                         2),
    ({"offset":     1},                         USERS_COUNT),
]

filter_data_default = [
    (None,                                      4),
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

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data_multiple)
async def test_get_users_list_with_filters_multiple(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_multiple_test_users_with_tokens: list[tuple[User, str]],
        role: UserRole,
        filter_params: dict[str, str | int],
        expected_count: int
):
    
    route = "/api/v1/users/list"
    await check_list_responces(
        client_async, user_factory, token_factory, role, route, 
        expected_count=expected_count,
        is_total_count=False, 
        is_parametrized=(filter_params is not None),
        filter_params=filter_params,
        obj_type="users"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("filter_params, expected_count", filter_data_default)
async def test_get_users_list_with_filters_default(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_users: list[User],
        filter_params: dict[str, str | int],
        expected_count: int
):
    
    route = "/api/v1/users/list"
    await check_list_responces(
        client_async, user_factory, token_factory, UserRole.USER, route, 
        expected_count=expected_count,
        is_total_count=False, 
        is_parametrized=(filter_params is not None),
        filter_params=filter_params,
        obj_type="users"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data_multiple)
async def test_get_users_list_count_with_filters_multiple(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_multiple_test_users_with_tokens: list[tuple[User, str]],
        role: UserRole,
        filter_params: dict[str, str | int],
        expected_count: int
):
    
    route = "/api/v1/users/list-count"
    await check_list_responces(
        client_async, user_factory, token_factory, role, route, 
        expected_count=expected_count,
        is_total_count=True, 
        is_parametrized=(filter_params is not None),
        filter_params=filter_params,
        obj_type="users"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("filter_params, expected_count", filter_data_default)
async def test_get_users_list_count_with_filters_default(
        client_async: AsyncClient,
        user_factory: UserFactory,
        token_factory: TokenFactory,
        create_test_users: list[User],
        filter_params: dict[str, str | int],
        expected_count: int
):
    
    route = "/api/v1/users/list-count"
    await check_list_responces(
        client_async, user_factory, token_factory, UserRole.USER, route, 
        expected_count=expected_count,
        is_total_count=True, 
        is_parametrized=(filter_params is not None),
        filter_params=filter_params,
        obj_type="users"
    )
