import logging
from logging.config import dictConfig

from alembic.config import Config
from alembic import command
from typing import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine

from src.database import engine
from src.config import LogConfig, app_configs # type: ignore
from src.auth import router as auth_router

logger = logging.getLogger("root")

# def run_upgrade(connection, cfg):
#     cfg.attributes["connection"] = connection
#     command.upgrade(cfg, "head")

# async def run_async_upgrade(engin: AsyncEngine = engine):
#     async with engine.connect() as connection:
#         await connection.run_sync(run_upgrade, Config("./alembic.ini"))

@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    dictConfig(LogConfig().model_dump())
    logger.info("App is running...")
    # await run_async_upgrade()
    yield


app = FastAPI(**app_configs, lifespan=lifespan)

app.include_router(router=auth_router.router, prefix="/auth", tags=["auth"])


