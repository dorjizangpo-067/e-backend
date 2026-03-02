import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utilits import create_access_token
from app.env_loader import settings
from app.models.users import User


@pytest.fixture
async def student_headers(session: AsyncSession) -> dict[str, str]:
    user = User(
        name="Student",
        bio="",
        email="student@example.com",
        role="student",
        hashed_password="pw",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id, "name": user.name},
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
    )
    return {"Cookie": f"access_token={token}"}


@pytest.mark.asyncio
async def test_admin_required_endpoint_forbidden(
    client: AsyncClient, session: AsyncSession, student_headers: dict[str, str]
) -> None:
    # /categories/create requires admin
    response = await client.post(
        "/categories/", json={"name": "Forbidden"}, headers=student_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_teacher_required_endpoint_forbidden(
    client: AsyncClient, session: AsyncSession, student_headers: dict[str, str]
) -> None:
    # Create category otherwise we get 404 from body before permission check failure?
    # (Checking if permission check is indeed bypassed or if verify order is weird)
    from app.models.categories import Category

    category = Category(name="Math")
    session.add(category)
    await session.commit()

    # /courses/ create requires teacher or admin
    course_data = {
        "title": "Bad Course",
        "description": "Desc",
        "video_id": "vid",
        "category": "Math",
    }
    response = await client.post("/courses/", json=course_data, headers=student_headers)
    assert response.status_code == 403
