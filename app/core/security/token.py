from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError, ExpiredSignatureError
from uuid import uuid4

from app.modules.db.base import Token

from app.core.config import settings
from app.modules.auth.token.exceptions import HTTPTokenExceptionInvalid, HTTPTokenExceptionExpired


async def jwt_create_token(data: dict, delta: timedelta, token_type: str) -> Token:

    expire = datetime.now(timezone.utc) + delta
    
    to_encode = data.copy()
    to_encode.update({
        "exp": expire, 
        "token_type": token_type,
        "jti": str(uuid4())
    })
    
    token_str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    token = Token(
        token=token_str, 
        user_id=data["user_id"], 
        token_type=token_type,
        expires_at=expire, 
        is_active=True
    )

    return token


async def jwt_create_access_token(data: dict) -> Token:
    delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return await jwt_create_token(data, delta, "access")


async def jwt_create_refresh_token(data: dict) -> Token:
    delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return await jwt_create_token(data, delta, "refresh")


def jwt_decode_token(token_str: str) -> dict:
    try:
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    
    except ExpiredSignatureError:
        raise HTTPTokenExceptionExpired()
    
    except JWTError:
        raise HTTPTokenExceptionInvalid()
    
def jwt_is_token_expired(token: Token) -> bool:
    try:
        jwt_decode_token(token.token)
    except HTTPTokenExceptionExpired:
        return True
    return False
    

def jwt_process_username_from_payload(
    payload: dict
) -> str:
    
    username = payload.get("sub")
    if username is None:
        raise HTTPTokenExceptionInvalid()
    
    return username
