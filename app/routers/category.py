from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import is_admin
from ..limiter import limiter
from ..models.categories import Category
from ..schemas.category import CategoryBaseSchema

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, CategoryBaseSchema],
)
@limiter.limit("10/minute")
async def create_category(
    request: Request,
    category: CategoryBaseSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    _=Depends(is_admin),  # noqa: ANN001
) -> dict:
    """Add category by admin"""
    db_category = Category(**category.model_dump(exclude_unset=True))
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return {"category": db_category}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_category(
    request: Request,
    categoty_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _=Depends(is_admin),  # noqa: ANN001
) -> None:
    """Add category by admin"""
    category = await db.get(Category, categoty_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoty Not found"
        )
    await db.delete(category)
    await db.commit()
    return
