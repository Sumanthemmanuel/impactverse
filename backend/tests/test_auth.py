import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuth:
    async def test_register(self, client: AsyncClient):
        data = {
            'email': 'newuser@example.com',
            'password': 'StrongPass1',
            'full_name': 'New User',
        }
        response = await client.post('/api/v1/auth/register', json=data)
        assert response.status_code == 201
        result = response.json()
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert result['token_type'] == 'bearer'

    async def test_register_duplicate_email(self, client: AsyncClient):
        data = {
            'email': 'dup@example.com',
            'password': 'StrongPass1',
            'full_name': 'First User',
        }
        await client.post('/api/v1/auth/register', json=data)
        response = await client.post('/api/v1/auth/register', json=data)
        assert response.status_code == 409

    async def test_register_weak_password(self, client: AsyncClient):
        data = {
            'email': 'weak@example.com',
            'password': 'weak',
            'full_name': 'Weak User',
        }
        response = await client.post('/api/v1/auth/register', json=data)
        assert response.status_code == 422

    async def test_login(self, client: AsyncClient):
        # Register first
        register_data = {
            'email': 'login@example.com',
            'password': 'LoginPass1',
            'full_name': 'Login User',
        }
        await client.post('/api/v1/auth/register', json=register_data)
        
        # Login
        login_data = {
            'email': 'login@example.com',
            'password': 'LoginPass1',
        }
        response = await client.post('/api/v1/auth/login', json=login_data)
        assert response.status_code == 200
        result = response.json()
        assert 'access_token' in result

    async def test_login_wrong_password(self, client: AsyncClient):
        register_data = {
            'email': 'wrongpw@example.com',
            'password': 'CorrectPass1',
            'full_name': 'Wrong PW User',
        }
        await client.post('/api/v1/auth/register', json=register_data)
        
        login_data = {
            'email': 'wrongpw@example.com',
            'password': 'WrongPass1',
        }
        response = await client.post('/api/v1/auth/login', json=login_data)
        assert response.status_code == 401

    async def test_get_me(self, client: AsyncClient, auth_headers: dict):
        response = await client.get('/api/v1/auth/me', headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result['email'] == 'testuser@example.com'
        assert result['full_name'] == 'Test User'

    async def test_get_me_unauthorized(self, client: AsyncClient):
        response = await client.get('/api/v1/auth/me')
        assert response.status_code in (401, 403)

    async def test_refresh_token(self, client: AsyncClient):
        # Register
        data = {
            'email': 'refresh@example.com',
            'password': 'RefreshPass1',
            'full_name': 'Refresh User',
        }
        reg_response = await client.post('/api/v1/auth/register', json=data)
        tokens = reg_response.json()
        
        # Refresh
        response = await client.post('/api/v1/auth/refresh', json={
            'refresh_token': tokens['refresh_token']
        })
        assert response.status_code == 200
        new_tokens = response.json()
        assert 'access_token' in new_tokens
