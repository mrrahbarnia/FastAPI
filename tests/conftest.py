import pytest
import pytest_asyncio
import asyncio

from functools import lru_cache
from typing import AsyncGenerator, Final, Generator
from httpx import AsyncClient, ASGITransport
from async_asgi_testclient import TestClient # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.database import Base, get_engine
from src.config import settings
from src.main import app

TEST_DB_URL: Final[str] = str(settings.POSTGRES_TEST_ASYNC_URL)
test_engine = create_async_engine(TEST_DB_URL)


@lru_cache
def override_get_engine() -> AsyncEngine:
    return test_engine

app.dependency_overrides[get_engine] = override_get_engine


@pytest_asyncio.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DB_URL)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _database_objects(db_engine: AsyncEngine):
    try:
        async with db_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield
    finally:
        async with db_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[TestClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app, client=("127.0.0.1", "8000")), base_url="http://test") as client: # type: ignore
        yield client