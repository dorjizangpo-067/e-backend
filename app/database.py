from sqlmodel import SQLModel, create_engine

from .env_loader import settings

engine = create_engine(settings.postgresql_url)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
