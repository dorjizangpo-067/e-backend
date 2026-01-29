from sqlmodel import SQLModel, create_engine

# from .models.categories import Category
# from .models.users import User
# from .models.courses import Course
from .env_loader import settings

engine = create_engine(settings.postgresql_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
