import pytest

from tests.test_config.classes.routes import BaseRoutesTest
from tests.test_config.utils.routes_utils import get_protected_routes

import tests.test_config.params.routes.account as params


@pytest.mark.usefixtures("client_async")
@pytest.mark.parametrize("protected_route", get_protected_routes(params.ROUTES), indirect=True)
class TestAccountRoutes(BaseRoutesTest):
    pass
