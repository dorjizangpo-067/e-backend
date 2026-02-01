import pytest
from httpx import AsyncClient
from sqlmodel import Session

from app.models.users import User


@pytest.mark.asyncio
async def test_get_users(client: AsyncClient, session: Session) -> None:
    # Create a user first
    user = User(
        name="Test User",
        email="test@example.com",
        role="student",
        hashed_password="hashed",
    )
    session.add(user)
    session.commit()

    response = await client.get("/users/")
    assert response.status_code == 200
    assert response.json() == {"message": "List of users"}
