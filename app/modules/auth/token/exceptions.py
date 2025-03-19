from fastapi import HTTPException, status


class HTTPTokenException(HTTPException):
    pass


class HTTPTokenExceptionInvalid(HTTPTokenException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class HTTPTokenExceptionExpired(HTTPTokenException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
