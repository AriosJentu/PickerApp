from typing import Optional

from pydantic import BaseModel, EmailStr, field_serializer, field_validator

from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.validators import UserValidator

from app.modules.user.data.schemas import UserDataRead, UserDataCreate, UserDataUpdateSecure, UserDataUpdate


class UserReadRegularNoData(BaseModel):
    id: int
    username: str
    role: UserRole


    @field_serializer("role")
    def serialize_role(self, value: UserRole) -> str:
        return str(value)


class UserReadRegular(UserReadRegularNoData):
    data: UserDataRead
    

class UserReadNoData(UserReadRegularNoData):
    email: EmailStr
    

class UserRead(UserReadRegular):
    email: EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    data: Optional[UserDataCreate] = None


    @field_validator("username")
    def validate_username(cls, username: str) -> str:
        return UserValidator.username(username)

    
    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        return UserValidator.password(password)

    
    @field_validator("email")
    def validate_email(cls, email: EmailStr) -> EmailStr:
        return UserValidator.email(email)
    

class UserUpdateSecure(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    data: Optional[UserDataUpdateSecure] = None
    
    
    @field_validator("username", mode="before")
    def validate_username(cls, username: Optional[str]) -> Optional[str]:
        return UserValidator.username(username)
    
    
    @field_validator("password", mode="before")
    def validate_password(cls, password: Optional[str]) -> Optional[str]:
        return UserValidator.password(password)
    
    
    @field_validator("email", mode="before")
    def validate_email(cls, email: Optional[EmailStr]) -> Optional[EmailStr]:
        return UserValidator.email(email)
    

class UserUpdate(UserUpdateSecure):
    data: Optional[UserDataUpdate] = None
    role: Optional[UserRole] = None


class UserResponce(UserReadNoData):
    detail: str


class UserListCountResponse(BaseModel):
    total_count: int
