from fastapi import HTTPException, status

from app.enums.user import UserRole


class HTTPUserException(HTTPException):
    pass


class HTTPUserExceptionUsernameAlreadyExists(HTTPUserException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists"
        )


class HTTPUserExceptionEmailAlreadyExists(HTTPUserException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )


class HTTPUserExceptionNotFound(HTTPUserException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


class HTTPUserExceptionNoDataProvided(HTTPUserException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class HTTPUserExceptionAlreadyLoggedIn(HTTPUserException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already logged in",
        )    


class HTTPUserExceptionIncorrectData(HTTPUserException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        ) 
        
        
class HTTPUserExceptionIncorrectFormData(HTTPUserException):
    def __init__(self, detail: str = "Username must be at least 3 characters long"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        ) 


class HTTPUserUnauthorized(HTTPUserException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )    


class HTTPUserExceptionAccessDenied(HTTPUserException):
    def __init__(self, role: UserRole):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: {role.name.lower()} role required"
        )


class HTTPUserInternalError(HTTPUserException):
    def __init__(self, description: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process user operation: {description}"
        )
