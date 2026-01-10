from sqlmodel import Session
from pydantic_settings import BaseSettings

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