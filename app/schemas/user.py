from pydantic import BaseModel, field_validator
from typing import Optional

from app.enums.user import UserRole


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    external_id: Optional[str]
    role: UserRole

    @field_validator("role")
    def serialize_role(cls, value: UserRole) -> str:
        return str(value)


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    external_id: Optional[str] = None


class UserUpdateSecure(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    external_id: Optional[str] = None
    

class UserUpdate(UserUpdateSecure):
    role: Optional[UserRole] = None


class UserResponce(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    detail: str


class UserListCountResponse(BaseModel):
    total_count: int
