from app.enums.user import UserRole


def get_exists_status_error_params(name: str):
    return [
        (True,  200,    ""),
        (False, 404,    f"{name} not found"),
    ]


def get_user_creator_access_error_params(name: str):
    return [
        (UserRole.ADMIN,        False,  200,    ""),
        (UserRole.MODERATOR,    False,  200,    ""),
        (UserRole.USER,         True,   200,    ""),
        (UserRole.USER,         False,  403,    f"No access to control {name}"),
    ]

def get_role_status_response_for_admin_params():
    return [
        (UserRole.USER,         403,    "Access denied"),
        (UserRole.MODERATOR,    403,    "Access denied"),
        (UserRole.ADMIN,        200,    "")
    ]
