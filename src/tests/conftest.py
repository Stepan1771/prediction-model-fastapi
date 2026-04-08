import base64

import pytest
import pytest_asyncio

from httpx import (
    AsyncClient,
    ASGITransport,
)

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool

from main import create_app

from models.base import Base

from api.depends.session import get_db

from api.depends.ml import get_ml_service

from services import MLService


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def engine():
    _engine = create_async_engine(TEST_DB_URL, poolclass=StaticPool)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    factory = async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    async with factory() as session:
        yield session


class MockMLService(MLService):
    def __init__(self) -> None:
        pass

    async def predict(self, schema) -> int:
        return 1


@pytest_asyncio.fixture
async def client(db_session):
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_ml_service] = lambda: MockMLService()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client) -> dict:
    creds = {
        "username": "fixture_user",
        "password": "Fixture999!"
    }
    resp = await client.post("/api/v1/auth/register", json=creds)
    assert resp.status_code == 201
    return creds


def basic_auth(username: str, password: str) -> dict:
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}

