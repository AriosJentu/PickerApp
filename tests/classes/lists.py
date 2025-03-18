import pytest

from httpx import AsyncClient

from app.modules.auth.user.enums import UserRole

from tests.types import InputData
from tests.factories.general_factory import GeneralFactory
from tests.utils.test_lists import check_list_responces


class BaseListsTest:
    route: str = None
    route_count: str = None
    obj_type: str = None

    @pytest.mark.asyncio
    async def test_list_with_filters(
            self,
            client_async: AsyncClient,
            general_factory: GeneralFactory,
            filter_params: InputData,
            expected_count: int,
            role: UserRole
    ):
        await check_list_responces(
            client_async, general_factory, role, self.route, 
            expected_count=expected_count,
            is_total_count=False, 
            filter_params=filter_params,
            obj_type=self.obj_type
        )

    @pytest.mark.asyncio
    async def test_list_count_with_filters(
            self,
            client_async: AsyncClient,
            general_factory: GeneralFactory,
            filter_params: InputData,
            expected_count: int,
            role: UserRole
    ):
        await check_list_responces(
            client_async, general_factory, role, self.route_count, 
            expected_count=expected_count,
            is_total_count=True, 
            filter_params=filter_params,
            obj_type=self.obj_type
        )
