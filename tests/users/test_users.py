import pytest
from httpx import AsyncClient

from tests.conftest import create_test_user


@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/api/users/create", json={"email": "test@example.com"}
    )
    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


@pytest.mark.anyio
async def test_create_user_duplicated_email(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users/create", json={"email": "test@example.com", "password": "sarasa12"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/api/users/create", json={"email": "test2@example.com", "password": "sarasa12"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test2@example.com"
    assert "id" in data
    assert "password_hash" not in data
