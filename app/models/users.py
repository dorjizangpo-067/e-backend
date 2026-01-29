from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .courses import Course


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    bio: str | None = Field(default=None)
    email: str = Field(index=True, unique=True)
    role: str
    hashed_password: str

    courses: List["Course"] = Relationship(
        sa_relationship=relationship("Course", back_populates="author")
    )
