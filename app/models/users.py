from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .courses import Course


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    bio: Mapped[str] = mapped_column(String(160), default=None)
    email: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    role: Mapped[str] = mapped_column(String(50))
    hashed_password: Mapped[str]

    courses: Mapped[List[Course]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
