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


@pytest.mark.anyio
async def test_patch_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    first_post_response = await client.post(
        "/api/notifications/create",
        json={
            "title": "Test notification",
            "content": "This is a test notification for the API.",
            "channel": "email",
        },
        headers=headers,
    )

    first_post_id = first_post_response.json()["id"]
    response = await client.patch(
        f"/api/notifications/patch/{first_post_id}",
        json={
            "title": "Test notification patch",
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Test notification patch"
    assert data["content"] == "This is a test notification for the API."


@pytest.mark.anyio
async def test_patch_fail_unauthorized(client: AsyncClient):
    response = await client.patch(
        "/api/notifications/patch/1",
        json={"title": "Unauthorized update"},
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_patch_fail_not_found(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.patch(
        "/api/notifications/patch/1",
        json={
            "title": "Test notification not found",
        },
        headers=headers,
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_patch_fail_forbiden(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    owner_headers = auth_header(token)

    notification_response = await client.post(
        "/api/notifications/create",
        json={
            "title": "Test notification",
            "content": "This is a test notification.",
            "channel": "email",
        },
        headers=owner_headers,
    )
    assert notification_response.status_code == 201, notification_response.text
    notification_id = notification_response.json()["id"]

    await create_test_user(client, email="email2@test.com")
    token2 = await login_user(client, email="email2@test.com")
    other_user_headers = auth_header(token2)

    response = await client.patch(
        f"/api/notifications/patch/{notification_id}",
        json={"title": "Unauthorized update"},
        headers=other_user_headers,
    )

    assert response.status_code == 403

@pytest.mark.anyio
async def test_delete_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.post(
        "api/notifications/create",
        json={
            "title": "test delete",
            "content": "This is a test notification for the API.",
            "channel": "email",
        },
        headers=auth_header(token)
    )

    assert response.status_code == 201

    to_delete_id = response.json()["id"]

    response = await client.delete(
            f"api/notifications/delete/{to_delete_id}",
            headers=auth_header(token)
        )

    assert response.status_code == 204

@pytest.mark.anyio
async def test_delete_unauthorized(client:AsyncClient):
    response = await client.delete(
                "api/notifications/delete/1"
            )
    
    assert response.status_code == 401

@pytest.mark.anyio
async def test_delete_not_existing(client:AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.delete(
                "api/notifications/delete/1",
                headers=auth_header(token)
            )

    assert response.status_code == 204

@pytest.mark.anyio
async def test_delete_forbiden(client: AsyncClient):
    await create_test_user(client)
    owner_token = await login_user(client)
    owner_auth = auth_header(owner_token)

    response = await client.post(
        "api/notifications/create",
        json={
            "title": "test delete",
            "content": "This is a test notification for the API.",
            "channel": "email",
        },
        headers=owner_auth
    )

    assert response.status_code == 201
    to_delete_id = response.json()["id"]

    await create_test_user(client, email="test_user@email.com")
    other_token = await login_user(client, email="test_user@email.com")
    other_auth = auth_header(other_token)

    response = await client.delete(
        f"api/notifications/delete/{to_delete_id}",
        headers=other_auth
    )

    assert response.status_code == 403