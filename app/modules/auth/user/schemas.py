from typing import Optional

from pydantic import BaseModel, EmailStr, field_serializer, field_validator

from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.validators import UserValidator


class UserReadRegular(BaseModel):
    id: int
    username: str
    role: UserRole

    @field_serializer("role")
    def serialize_role(self, value: UserRole) -> str:
        return str(value)
    

class UserRead(UserReadRegular):
    email: EmailStr
    external_id: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    external_id: Optional[str] = None


    @field_validator("username")
    def validate_username(cls, username: str):
        return UserValidator.username(username)

    
    @field_validator("password")
    def validate_password(cls, password: str):
        return UserValidator.password(password)

    
    @field_validator("email")
    def validate_email(cls, email: EmailStr):
        return UserValidator.email(email)
    

class UserUpdateSecure(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    external_id: Optional[str] = None
    
    
    @field_validator("username", mode="before")
    def validate_username(cls, username: Optional[str]):
        return UserValidator.username(username)
    
    
    @field_validator("password", mode="before")
    def validate_password(cls, password: Optional[str]):
        return UserValidator.password(password)
    
    
    @field_validator("email", mode="before")
    def validate_email(cls, email: Optional[EmailStr]):
        return UserValidator.email(email)
    

class UserUpdate(UserUpdateSecure):
    role: Optional[UserRole] = None


class UserResponce(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    detail: str


class UserListCountResponse(BaseModel):
    total_count: int
