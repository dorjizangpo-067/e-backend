from sqlmodel import Session
from pydantic_settings import BaseSettings
from fastapi import Request
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, InvalidSignatureError

from .database import engine
class Settings(BaseSettings):
    sqlite_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

def get_session():
    with Session(engine) as session:
        yield session

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