import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.database import get_db
from app.models import Base
from app.config import settings

# Use a test database
TEST_DATABASE_URL = str(settings.DATABASE_URL).replace('/impactverse_db', '/impactverse_test_db')

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='function')
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with test_session_factory() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope='function')
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    """Get auth headers by registering and logging in a test user."""
    register_data = {
        'email': 'testuser@example.com',
        'password': 'TestPass123',
        'full_name': 'Test User',
        'role': 'citizen',
    }
    response = await client.post('/api/v1/auth/register', json=register_data)
    tokens = response.json()
    return {'Authorization': f'Bearer {tokens["access_token"]}'}


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, db_session: AsyncSession):
    """Get admin auth headers."""
    register_data = {
        'email': 'admin@example.com',
        'password': 'AdminPass123',
        'full_name': 'Admin User',
        'role': 'platform_admin',
    }
    response = await client.post('/api/v1/auth/register', json=register_data)
    tokens = response.json()
    return {'Authorization': f'Bearer {tokens["access_token"]}'}
