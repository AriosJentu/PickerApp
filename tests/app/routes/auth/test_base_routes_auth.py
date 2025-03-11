import pytest

from tests.classes.routes import BaseRoutesTest

import tests.params.routes.auth as params
from tests.utils.routes_utils import get_protected_routes


@pytest.mark.usefixtures("client_async")
@pytest.mark.parametrize("protected_route", get_protected_routes(params.ROUTES), indirect=True)
class TestAuthRoutes(BaseRoutesTest):
    pass
