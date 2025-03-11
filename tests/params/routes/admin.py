from tests.constants import Roles


ROUTES = [
    ("DELETE",  "/api/v1/admin/clear-tokens", Roles.ADMIN),
]

ADMIN_TOKENS_RESPONSE = ["inactive tokens from base"]
