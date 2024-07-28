from redis import Redis

from typing import AsyncGenerator, Any
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData, INTEGER, String, Insert, Update, Select, CursorResult, Delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection

from src.constants import DB_NAMING_CONVENTION # type: ignore
from src.config import settings # type: ignore
from src.auth import types # type: ignore

POSTGRES_URL = str(settings.POSTGRES_ASYNC_URL)
REDIS_PORT = settings.REDIS_PORT
REDIS_HOST = settings.REDIS_HOST

engine = create_async_engine(POSTGRES_URL)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
    type_annotation_map = {
        types.UserId: INTEGER,
        types.Email: String
    }


async def get_db_connection() -> AsyncGenerator:
    connection = await engine.connect()
    try:
        yield connection
    finally:
        await connection.close()


def get_redis_connection() -> Redis:
    return Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


async def fetch_one(
        query: Select | Insert | Update,
        db_connection: AsyncConnection | None = None,
        commit_after: bool = False
) -> dict[str, Any] | None:
    if not db_connection:
        async with engine.connect() as conn:
            cursor = await _execute_query(query=query, db_connection=conn, commit_after=commit_after)
            return cursor.first()._asdict() if cursor.rowcount > 0 else None # type: ignore
    cursor = await _execute_query(query=query, db_connection=db_connection, commit_after=commit_after)
    return cursor.first()._asdict() if cursor.rowcount > 0 else None # type: ignore


async def fetch_all(
        query: Select | Insert | Update,
        db_connection: AsyncConnection | None = None,
        commit_after: bool = False
) -> list[dict[str, Any]]:
    if not db_connection:
        async with engine.connect() as conn:
            cursor = await _execute_query(query=query, db_connection=conn, commit_after=commit_after)
            return [r._asdict() for r in cursor.all()]

    cursor = await _execute_query(query=query, db_connection=db_connection, commit_after=commit_after)
    return [r._asdict() for r in cursor.all()]


async def execute(
        query: Insert | Update | Delete,
        db_connection: AsyncConnection | None = None,
        commit_after: bool = False
) -> CursorResult:
    if not db_connection:
        async with engine.connect() as conn:
            return await _execute_query(query=query, db_connection=conn, commit_after=commit_after)
    return await _execute_query(query=query, db_connection=db_connection, commit_after=commit_after)


async def _execute_query(
        *,
        query: Insert | Update | Select | Delete,
        db_connection: AsyncConnection,
        commit_after: bool = False
) -> CursorResult:
    result = await db_connection.execute(query)
    if commit_after:
        await db_connection.commit()
    return result
    
