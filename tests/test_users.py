import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User


@pytest.mark.asyncio
async def test_get_users(client: AsyncClient, session: AsyncSession) -> None:
    # Create a user first
    user = User(
        name="Test User",
        bio="",
        email="test@example.com",
        role="student",
        hashed_password="hashed",
    )
    session.add(user)
    await session.commit()

    response = await client.get("/users/")
    assert response.status_code == 200
    assert response.json() == {"message": "List of users"}
