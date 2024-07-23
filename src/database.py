from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData, INTEGER, UUID, String
from sqlalchemy.ext.asyncio import create_async_engine

from src.constants import DB_NAMING_CONVENTION # type: ignore
from src.config import settings # type: ignore
from src.auth import types # type: ignore

POSTGRES_URL = str(settings.POSTGRES_ASYNC_URL)

engine = create_async_engine(POSTGRES_URL,pool_recycle=60*20, pool_size=16, pool_pre_ping=True)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
    type_annotation_map = {
        types.UserId: INTEGER,
        types.ProfileId: UUID,
        types.Email: String
    }


async def get_db_connection() -> AsyncGenerator:
    connection = await engine.connect()
    try:
        yield connection
    finally:
        await connection.close()
