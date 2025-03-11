from tests.constants import Roles


ROUTES = [
    ("GET",     "/api/v1/account/",             Roles.ALL_ROLES),
    ("PUT",     "/api/v1/account/",             Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/account/",             Roles.ALL_ROLES),
    ("GET",     "/api/v1/account/check-token",  Roles.ALL_ROLES),
]

UPDATE_USER_DATA_STATUS_ERROR = [
    ({"email":      "updated_email@example.com"},                                   200,    ""), 
    ({"username":   "newusername"},                                                 200,    ""), 
    ({"password":   "NewPassword123!"},                                             200,    ""),
    ({"email":      "updated_email@example.com",    "username":     "newusername"}, 200,    ""), 
    ({"email":      "invalid-email"},                                               422,    "Invalid email format"),
    ({"username":   ""},                                                            422,    "Username must be at least 3 characters long."),
    ({"password":   "weakpass"},                                                    422,    "Password must contain"),
    ({"email":      "invalid-email",                "username":     ""},            422,    "Username must be at least 3 characters long."), 
]

UPDATE_USER_DUPLICATE_EMAIL_EXPECT_ERROR = [
    (False, 200,    ""),
    (True,  400,    "User with this email already exists"),
]

UPDATE_USER_DUPLICATE_USERNAME_EXPECT_ERROR = [
    (False, 200,    ""),
    (True,  400,    "User with this username already exists"),
]
