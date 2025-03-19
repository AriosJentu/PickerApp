import pytest

from httpx import AsyncClient

from app.modules.auth.user.enums import UserRole

from tests.utils.types import RouteBaseFixture
from tests.utils.constants import Roles
from tests.factories.general_factory import GeneralFactory
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users


class BaseRoutesTest:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("role", Roles.LIST)
    async def test_routes_access(
            self,
            client_async: AsyncClient,
            general_factory: GeneralFactory,
            protected_route: RouteBaseFixture,
            role: UserRole
    ):
        await check_access_for_authenticated_users(client_async, general_factory, protected_route, role)

    @pytest.mark.asyncio
    async def test_routes_require_auth(
            self,
            client_async: AsyncClient,
            protected_route: RouteBaseFixture,
    ):
        await check_access_for_unauthenticated_users(client_async, protected_route)
