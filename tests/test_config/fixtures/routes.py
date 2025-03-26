import pytest

from tests.test_config.utils.types import RouteBaseFixture


@pytest.fixture
def protected_route(request) -> RouteBaseFixture:
    return request.param
