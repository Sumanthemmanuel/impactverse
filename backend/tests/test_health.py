import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealth:
    async def test_health_endpoint(self, client: AsyncClient):
        response = await client.get('/health')
        assert response.status_code == 200
        result = response.json()
        assert result['status'] == 'healthy'
        assert 'version' in result
