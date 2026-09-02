import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestChallenges:
    async def test_create_challenge(self, client: AsyncClient, auth_headers: dict):
        data = {
            'title': 'Water contamination in village XYZ causing health issues',
            'narrative': 'The drinking water supply in village XYZ has been contaminated with heavy metals. Over 500 families are affected and several children have fallen ill.',
            'domain': 'water',
            'severity': 'high',
            'district': 'Ranchi',
            'affected_population': 2500,
        }
        response = await client.post('/api/v1/challenges/', json=data, headers=auth_headers)
        assert response.status_code == 201
        result = response.json()
        assert result['title'] == data['title']
        assert result['status'] == 'submitted'
        assert 'id' in result

    async def test_list_challenges(self, client: AsyncClient, auth_headers: dict):
        # Create a challenge first
        data = {
            'title': 'Road damage near school requires immediate repair',
            'narrative': 'The main road connecting the school to the village has multiple large potholes making it dangerous for children.',
            'domain': 'infrastructure',
        }
        await client.post('/api/v1/challenges/', json=data, headers=auth_headers)
        
        response = await client.get('/api/v1/challenges/')
        assert response.status_code == 200
        result = response.json()
        assert 'items' in result
        assert 'total' in result

    async def test_get_challenge(self, client: AsyncClient, auth_headers: dict):
        # Create
        data = {
            'title': 'Healthcare facility shortage in remote block area',
            'narrative': 'There is no primary healthcare center within 30km radius of this tribal block. Expecting mothers have to travel very far.',
            'domain': 'healthcare',
            'severity': 'critical',
        }
        create_resp = await client.post('/api/v1/challenges/', json=data, headers=auth_headers)
        challenge_id = create_resp.json()['id']
        
        # Get
        response = await client.get(f'/api/v1/challenges/{challenge_id}')
        assert response.status_code == 200
        assert response.json()['id'] == challenge_id

    async def test_create_challenge_validation(self, client: AsyncClient, auth_headers: dict):
        # Too short title
        data = {
            'title': 'Short',
            'narrative': 'This is a test narrative that is long enough to pass validation.',
            'domain': 'water',
        }
        response = await client.post('/api/v1/challenges/', json=data, headers=auth_headers)
        assert response.status_code == 422
