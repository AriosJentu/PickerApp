from fastapi import HTTPException, status


class HTTPLobbyException(HTTPException):
    pass


class HTTPLobbyAlgorithmNotFound(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Algorithm not found",
        )


class HTTPLobbyNotFound(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found",
        )


class HTTPLobbyAccessDenied(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lobby not found",
        )
