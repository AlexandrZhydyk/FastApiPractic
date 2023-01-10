import asyncio
import os

import alembic
import pytest
import pytest_asyncio
from alembic.config import Config
from fastapi import FastAPI
from httpx import AsyncClient

os.environ['TESTING'] = 'True'

from src.db.base import async_session, init_tables, delete_tables
from src.db.models.users import User
from src.schemas.user import UserOut
from src.core.security import create_access_token, hash_password


@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
# @pytest.mark.asyncio
async def app() -> FastAPI:
    from src.main import get_application  # local import for testing purpose

    app = get_application()
    yield app


@pytest.fixture(scope="module")
async def session():
    await init_tables()
    session = async_session()
    yield session
    await delete_tables()



# @pytest.fixture(autouse=True)
# def db_models():
#     config = Config("alembic.ini")
#     alembic.command.upgrade(config, "head")
#     yield
#     alembic.command.downgrade(config, "base")



@pytest.fixture(scope="module")
async def create_user(session):
    db_obj = User(
        email="test@test.com",
        name="Test",
        is_active=True,
        hashed_password=hash_password("testpass")
    )
    session.add(db_obj)
    await session.commit()
    return db_obj

# @pytest.fixture
# async def create_company(session):
#     db_obj = User(
#         email="company@test.com",
#         name="Test",
#         is_company=True,
#         is_active=True,
#         hashed_password=hash_password("testpass")
#     )
#     session.add(db_obj)
#     await session.commit()
#     return db_obj

@pytest.fixture(scope="module")
async def create_superuser(session):
    db_obj = User(
        email="superuser@test.com",
        name="Test",
        is_active=True,
        is_superuser=True,
        hashed_password=hash_password("superuserpass")
    )
    session.add(db_obj)
    await session.commit()
    return db_obj


@pytest.fixture
def token(create_user: UserOut) -> str:
    access_token = create_access_token(data={"sub": create_user.email, "scopes": ["auth"]})
    return access_token


# @pytest.fixture
# def company_token(create_company: UserOut) -> str:
#     access_token = create_access_token(data={"sub": create_company.email, "scopes": ["auth", "company"]})
#     return access_token


@pytest.fixture
def superuser_token(create_superuser: UserOut) -> str:
    access_token = create_access_token(data={"sub": create_superuser.email, "scopes": ["auth", "superuser"]})
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
def authorized_client(client: AsyncClient, token: str) -> AsyncClient:
    client.headers = {
        "Authorization": f"Bearer {token}",
        **client.headers,
    }
    return client


# @pytest.fixture
# def company_client(client: AsyncClient, company_token: str) -> AsyncClient:
#     client.headers = {
#         "Authorization": f"Bearer {company_token}",
#         **client.headers,
#     }
#     return client


@pytest.fixture
def superuser_client(client: AsyncClient, superuser_token: str) -> AsyncClient:
    client.headers = {
        "Authorization": f"Bearer {superuser_token}",
        **client.headers,
    }
    return client


# @pytest.mark.asyncio
# async def test_create_job(company_client):
#
#     job = {"email": "test_user@test.com",
#            "title": "Test",
#            "description": "testpass",
#            "salary_from": 10,
#            "salary_to": 20,
#            }
#     resp = await company_client.post('jobs/', json=job)
#     assert resp.status_code == status.HTTP_200_OK
#     assert resp.json()["email"] == "test_user@test.com"
#     assert resp.json()["title"] == "Test"
#     assert resp.json()["description"] == True
#     assert resp.json()["salary_from"] == 10
#     assert resp.json()["salary_to"] == 20


