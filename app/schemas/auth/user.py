from typing import Optional

from pydantic import BaseModel, EmailStr, field_serializer, field_validator

from app.enums.user import UserRole
from app.core.security.validators import (
    validate_username, 
    validate_password, 
    validate_email
)


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    external_id: Optional[str] = None
    role: UserRole

    @field_serializer("role")
    def serialize_role(self, value: UserRole) -> str:
        return str(value)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    external_id: Optional[str] = None


    @field_validator("username")
    def validate_username(cls, username):
        return validate_username(username)

    
    @field_validator("password")
    def validate_password(cls, password):
        return validate_password(password)

    
    @field_validator("email")
    def validate_email(cls, email):
        return validate_email(email)
    

class UserUpdateSecure(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    external_id: Optional[str] = None
    
    
    @field_validator("username", mode="before")
    def validate_username(cls, username):
        return validate_username(username)
    
    
    @field_validator("password", mode="before")
    def validate_password(cls, password):
        return validate_password(password)
    
    
    @field_validator("email", mode="before")
    def validate_email(cls, email):
        return validate_email(email)
    

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
