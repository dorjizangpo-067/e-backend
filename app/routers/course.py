from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import (
    current_user_dependency,
    is_teacher_or_admin,
)
from ..limiter import limiter
from ..models.categories import Category
from ..models.courses import Course
from ..schemas.course import (
    CourseBaseSchema,
    CreateCourseSchema,
    ReadCourseSchema,
    UpdateCourseSchema,
)

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=dict[str, list[ReadCourseSchema]])
@limiter.limit("5/second")
@limiter.limit("100/hour")
async def get_courses(
    request: Request,  # for Limiter to perform
    db: Annotated[AsyncSession, Depends(get_db)],
    is_authorized: Annotated[bool, Depends(current_user_dependency)],
    limit: Annotated[int, Query(le=25)] = 15,
    offset: int = 0,
) -> dict:
    """Retrieve a list of courses with pagination."""
    result = await db.execute(select(Course).offset(offset).limit(limit))
    courses = result.scalars()
    return {"courses": courses}


@router.post(
    "/", response_model=dict[str, CourseBaseSchema], status_code=status.HTTP_201_CREATED
)
@limiter.limit("3/second")
@limiter.limit("100/hour")
async def create_course(
    request: Request,
    course_in: CreateCourseSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(current_user_dependency)],
    is_authorized: Annotated[bool, Depends(is_teacher_or_admin)],
) -> dict:
    """Create a new course and assign it to the current user."""

    stmt = select(Category).where(Category.name == course_in.category)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()

    if not category:
        categories_result = await db.execute(select(Category.name))
        all_categories = categories_result.scalars().all()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Invalid category '{course_in.category}'",
                "available_categories": all_categories,
            },
        )

    # Prepare data and exclude 'category' string to replace with 'category_id'
    course_data = course_in.model_dump(exclude={"category"})
    db_course = Course(
        **course_data, category_id=category.id, author_id=int(current_user["id"])
    )

    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return {"courses": db_course}


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("2/minute")
async def delete_course(
    request: Request,
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(current_user_dependency)],
    is_authorized: Annotated[bool, Depends(is_teacher_or_admin)],
) -> None:
    """Delete a course by its ID"""
    course = await db.get(Course, course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Ownership check
    if str(course.author_id) != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this course",
        )

    await db.delete(course)
    await db.commit()
    return


@router.patch("/{course_id}", response_model=dict[str, CourseBaseSchema])
@limiter.limit("10/minute")  # Very strict
async def update_course(
    request: Request,
    course_id: int,
    course_update: UpdateCourseSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(current_user_dependency)],
    is_authorized: Annotated[bool, Depends(is_teacher_or_admin)],
) -> dict:
    """Update a course by its ID."""
    course = await db.get(Course, course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Ownership check
    if str(course.author_id) != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this course",
        )

    # Apply partial updates
    update_data = course_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)

    db.add(course)
    await db.commit()
    await db.refresh(course)
    return {"course": course}
