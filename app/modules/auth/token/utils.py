from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError, ExpiredSignatureError
from uuid import uuid4

from app.core.config import settings


class TokenManager:

    @staticmethod
    def create_data(username: str, user_id: int) -> dict:
        return {"sub": username, "user_id": user_id}
    

    @staticmethod
    def get_encode_data(data: dict, expires_in: timedelta, token_type: str) -> dict:
        expire = datetime.now(timezone.utc) + expires_in
    
        to_encode = data.copy()
        to_encode.update({
            "exp": expire, 
            "token_type": token_type,
            "jti": str(uuid4())
        })
    
        return to_encode


    @classmethod
    def get_encode_access_data(cls, data: dict) -> dict:
        delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return cls.get_encode_data(data, delta, "access")
    
    
    @classmethod
    def get_encode_refresh_data(cls, data: dict) -> dict:
        delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return cls.get_encode_data(data, delta, "refresh")


    @staticmethod
    def create_token(encode_data: dict) -> str:       
        return jwt.encode(encode_data.copy(), settings.SECRET_KEY, algorithm=settings.ALGORITHM)


    @staticmethod
    def decode_token(token_str: str) -> dict:
        try:
            payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        
        except ExpiredSignatureError:
            raise ValueError("Token has expired")
        
        except JWTError:
            raise ValueError("Invalid token")


    @classmethod
    def is_token_expired(cls, token_str: str) -> bool:
        try:
            cls.decode_token(token_str)
        
        except ValueError as e:
            if e.args[0] == "Token has expired":
                return True
            raise

        return False
    
    
    @classmethod
    def is_correct_type(cls, token_str: str, token_type: str, with_payload: bool = False) -> bool | tuple[bool, dict]:
        try:
            payload = cls.decode_token(token_str)
            result = payload.get("token_type") == token_type
            
            if with_payload:
                return result, payload
            return result
        
        except ValueError:
            raise


    @classmethod
    def get_username_from_token(cls, token_str: str, token_type: str) -> str:
        try:
            correct, payload = cls.is_correct_type(token_str, token_type)
            if not correct:
                raise ValueError("Invalid token")
        
            username = payload.get("sub")
            if not username:
                raise ValueError("Missing username in token")
            
            return username
        
        except ValueError:
            raise
