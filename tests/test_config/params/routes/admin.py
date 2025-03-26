from tests.test_config.utils.constants import Roles


ROUTES = [
    ("DELETE",  "/api/v1/admin/clear-tokens", Roles.ADMIN),
]
