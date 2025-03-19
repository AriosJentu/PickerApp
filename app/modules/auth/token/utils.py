from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError, ExpiredSignatureError
from uuid import uuid4

from app.core.config import settings
from app.modules.auth.token.exceptions import HTTPTokenExceptionInvalid, HTTPTokenExceptionExpired


class TokenManager:

    @staticmethod
    def create_data(username: str, user_id: int) -> dict:
        return {"sub": username, "user_id": user_id}
    

    @staticmethod
    def create_token(data: dict, expires_in: timedelta, token_type: str) -> str:
        expire = datetime.now(timezone.utc) + expires_in
    
        to_encode = data.copy()
        to_encode.update({
            "exp": expire, 
            "token_type": token_type,
            "jti": str(uuid4())
        })
        
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


    @classmethod
    def create_access_token(cls, data: dict) -> str:
        delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return cls.create_token(data, delta, "access")


    @classmethod
    def create_refresh_token(cls, data: dict) -> str:
        delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return cls.create_token(data, delta, "refresh")


    @staticmethod
    def decode_token(token_str: str) -> dict:
        try:
            payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        
        except ExpiredSignatureError:
            raise HTTPTokenExceptionExpired()
        
        except JWTError:
            raise HTTPTokenExceptionInvalid()


    @classmethod
    def is_token_expired(cls, token_str: str) -> bool:
        try:
            cls.decode_token(token_str)
        
        except HTTPTokenExceptionExpired:
            return True
        
        return False


    @classmethod
    def get_username_from_token(cls, token_str: str) -> str:
        payload = cls.decode_token(token_str)
        username = payload.get("sub")
        
        if not username:
            raise HTTPTokenExceptionInvalid()
        
        return username
