import pytest

from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.classes.routes import BaseRoutesTest
from tests.factories.general_factory import GeneralFactory

import tests.params.routes.admin as params
from tests.params.routes.common import get_role_status_response_for_admin_params
from tests.utils.routes_utils import get_protected_routes


@pytest.mark.usefixtures("client_async")
@pytest.mark.parametrize("protected_route", get_protected_routes(params.ROUTES), indirect=True)
class TestAdminRoutes(BaseRoutesTest):
    pass


@pytest.mark.asyncio
@pytest.mark.parametrize("tokens_response_substr", params.ADMIN_TOKENS_RESPONSE)
@pytest.mark.parametrize("role, expected_status, response_substr", get_role_status_response_for_admin_params())
async def test_clear_inactive_tokens(
        client_async: AsyncClient, 
        general_factory: GeneralFactory,
        response_substr: str,
        tokens_response_substr: str,
        expected_status: int,
        role: UserRole,
):
    
    route = "/api/v1/admin/clear-tokens"
    base_user_data = await general_factory.create_base_user(role)

    response: Response = await client_async.delete(route, headers=base_user_data.headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if expected_status == 200:
        assert tokens_response_substr in str(json_data["detail"]), f"Unexpected response data: {json_data}"
        return 
    
    assert response_substr in str(json_data["detail"]), f"Unexpected response data: {json_data}"
