import asyncio
import os

import alembic
import pytest
import pytest_asyncio
from alembic.config import Config
from fastapi import FastAPI
from httpx import AsyncClient

os.environ['TESTING'] = 'True'

from src.db.base import async_session
from src.db.models.users import User
from src.schemas.user import UserOut
from src.core.security import create_access_token, hash_password


@pytest.fixture(scope="session")
def app() -> FastAPI:
    from src.main import get_application  # local import for testing purpose

    app = get_application()
    return app


@pytest_asyncio.fixture(scope="session")
async def session():
    session = async_session()
    return session


@pytest.fixture(autouse=True)
def db_models():
    config = Config("alembic.ini")
    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


@pytest.fixture
async def test_client(session):
    db_obj = User(
        email="test@test.com",
        name="Test",
        is_company=True,
        is_active=True,
        hashed_password=hash_password("testpass")
    )
    session.add(db_obj)
    await session.commit()
    return db_obj


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def token(test_client: UserOut) -> dict:
    access_token = create_access_token(data={"sub": test_client.email, "scopes": ["auth"]})
    return access_token


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(
        app=app,
        base_url="http://localhost",
        headers={"Content-Type": "application/json"}
    ) as client:
        yield client


@pytest.fixture
def authorized_client(client: AsyncClient, token: dict) -> AsyncClient:
    client.headers = {
        "Authorization": f"Bearer {token}",
        **client.headers,
    }
    return client



