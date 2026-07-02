"""
Shared test fixtures.
Tests use an in-memory SQLite database so no external DB is needed.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import Base, get_db

# Use SQLite for tests (fast, no setup needed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client):
    """Register and log in a test user, return Authorization headers."""
    await client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+91 98765 43210",
        "password": "TestPass@123",
    })
    response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass@123",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
