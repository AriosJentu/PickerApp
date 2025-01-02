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


class HTTPTokenExceptionInvalidType(HTTPTokenException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token type",
            headers={"WWW-Authenticate": "Bearer"},
        )


class HTTPTokenExceptionInvalidOrExpired(HTTPTokenException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token is invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
