from typing import Optional
from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.types import InputData
from tests.factories.general_factory import GeneralFactory


async def check_list_responces(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        role: UserRole,
        route: str,
        expected_count: int = 0,
        is_total_count: bool = False,
        filter_params: Optional[InputData] = None, 
        obj_type: str = ""
):
    is_parametrized = (filter_params is not None)
    if is_parametrized and is_total_count and any(
            key in filter_params.keys() 
            for key in ("limit", "offset", "sort_by", "sort_order")
    ):
        return

    base_user_data = await general_factory.create_base_user(role)
    response: Response = await client_async.get(route, headers=base_user_data.headers, params=filter_params)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    json_data = response.json()
    response_count = 0
    if is_total_count:
        response_count = json_data["total_count"]
    else:
        response_count = len(json_data)

    error_msg = f"Expected {expected_count} {obj_type}, got {response_count}"
    if is_parametrized:
        error_msg = f"Expected {expected_count} {obj_type} for filter `{filter_params}`, got {response_count}"

    assert response_count == expected_count, error_msg
