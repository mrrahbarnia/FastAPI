from redis import Redis
from functools import lru_cache
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from sqlalchemy.types import INTEGER, String, UUID, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from src.constants import DB_NAMING_CONVENTION # type: ignore
from src.config import settings # type: ignore
from src.auth import types # type: ignore
from src.contacts.types import ContactId

POSTGRES_URL = str(settings.POSTGRES_ASYNC_URL)
REDIS_PORT = settings.REDIS_PORT
REDIS_HOST = settings.REDIS_HOST

engine: AsyncEngine = create_async_engine(POSTGRES_URL)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
    type_annotation_map = {
        types.UserId: INTEGER,
        types.Email: String,
        ContactId: UUID,
        datetime: DateTime(timezone=True)
    }

@lru_cache
def get_engine() -> AsyncEngine:
    return engine


def get_redis_connection() -> Redis:
    return Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
