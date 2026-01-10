from fastapi import Request
from pwdlib import PasswordHash

import jwt
from datetime import datetime, timezone, timedelta
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, InvalidSignatureError
from ..schemas.user import TokenResponseSchema

hashed_hasdher = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    """hash plain password"""
    return hashed_hasdher.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verify plain password with hashed password"""
    return hashed_hasdher.verify(plain_password, hashed_password)

def create_access_token(data: dict, secret_key: str, algorithm: str, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_access_token(token: str, secret_key: str, algorithms: list[str]) -> dict | None:
    """Verify a JWT access token and return the payload if valid."""
    try:
        data = jwt.decode(token, secret_key, algorithms=algorithms)
        return data
    except ExpiredSignatureError:
        return None
    except InvalidSignatureError:
        return None
    except InvalidTokenError:
        return None

def get_current_user(request: Request, secret_key: str, algorithms: list[str]) -> dict | None:
    """Get the current user from the JWT token."""
    try: 
        token = request.cookies.get("access_token")
    except AttributeError:
        return None
    if not token:
        return None
    payload = verify_access_token(token, secret_key, algorithms)
    if payload is None:
        return None
    return payload