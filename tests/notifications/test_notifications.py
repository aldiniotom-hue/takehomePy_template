import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, create_test_user, login_user


@pytest.mark.anyio
async def test_create_notification_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.post(
        "/api/notifications/create",
        json={
            "title": "Test notification",
            "content": "This is a test notification for the API.",
            "channel": "email",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test notification"
    assert data["content"] == "This is a test notification for the API."
    assert "id" in data

@pytest.mark.anyio
async def test_create_fail_unauthorized(client: AsyncClient):
    response = await client.post(
            "/api/notifications/create",
            json={
                "title": "Test notification",
                "content": "This is a test notification for the API.",
                "channel": "email",
            },
        )

    assert response.status_code == 401

