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
