from fastapi import HTTPException, status


class HTTPLobbyException(HTTPException):
    pass


class HTTPLobbyAlgorithmNotFound(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Algorithm not found",
        )


class HTTPLobbyAlgorithmUpdateDataNotProvided(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Algorithm update data not provided",
        )


class HTTPLobbyNotFound(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found",
        )


class HTTPLobbyUpdateDataNotProvided(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lobby update data not provided",
        )


class HTTPLobbyAccessDenied(HTTPLobbyException):
    def __init__(self, data=None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to control lobby",
        )


class HTTPLobbyTeamAccessDenied(HTTPLobbyException):
    def __init__(self, data=None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to control team",
        )


class HTTPTeamCreatingFailed(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create team",
        )
        

class HTTPAlgorithmCreatingFailed(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create algorithm",
        )


class HTTPTeamNotFound(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )


class HTTPTeamUpdateDataNotProvided(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team update data not provided",
        )


class HTTPLobbyInternalError(HTTPLobbyException):
    def __init__(self, description: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process lobby operation: {description}"
        )


class HTTPLobbyAlgorithmAccessDenied(HTTPLobbyException):
    def __init__(self, data=None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to control algorithm",
        )


class HTTPLobbyUserAlreadyIn(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already in lobby"
        )


class HTTPLobbyParticipantNotFound(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )


class HTTPLobbyParticipantUpdateDataNotProvided(HTTPLobbyException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant update data not provided",
        )
