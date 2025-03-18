from pydantic import BaseModel

from app.modules.auth.user.enums import UserRole


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    

class TokenStatus(BaseModel):
    active: bool
    username: str
    email: str
    role: UserRole
    detail: str


class TokenCleanResponse(BaseModel):
    detail: str
