import datetime

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_post_health_test(client: AsyncClient):
    response = await client.post(
        "/api/healthtest/postHealthTest",
        json={
            "datetime": datetime.datetime.now().isoformat(),
            "message": "",
        },
    )

    assert response.status_code == 201


@pytest.mark.anyio
async def test_database_is_empty(client: AsyncClient):
    response = await client.post(
        "/api/healthtest/getHealthTest",
        json={
            "datetime": datetime.datetime.now().isoformat(),
            "message": "",
        },
    )

    data = response.json()
    assert data.length() == 0
