from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import is_admin
from ..limiter import limiter
from ..models.users import User
from ..schemas.user import UserReadSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=dict[str, list[UserReadSchema]],
    status_code=status.HTTP_302_FOUND,
)
@limiter.limit("10/minute")
async def get_users(
    request: Request,  # for Limiter to perform
    db: Annotated[AsyncSession, Depends(get_db)],
    is_admin: Annotated[bool, Depends(is_admin)],
    limit: Annotated[int, Query(le=25)] = 15,
    offset: int = 0,
) -> dict:
    """get all users"""
    result = await db.execute(select(User).offset(offset).limit(limit))
    users = result.scalars()
    return {"users": users}
