from app.enums.user import UserRole


def get_exists_status_error_params(name: str, with_empty_data: bool = False):
    result = [
        (True,  200,    ""),
        (False, 404,    f"{name} not found"),
    ]
    
    if with_empty_data:
        result.append( (None, 200, "") )
    
    return result


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
