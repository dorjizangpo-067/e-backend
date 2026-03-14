from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
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
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def get_users(
    request: Request,  # for Limiter to perform
    db: Annotated[AsyncSession, Depends(get_db)],
    is_admin: Annotated[bool, Depends(is_admin)],
    limit: Annotated[int, Query(le=25)] = 15,
    offset: int = 0,
) -> Page[UserReadSchema]:
    """get all users"""
    query = select(User)
    return await paginate(db, query)
