import logging
from logging.config import dictConfig

from typing import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager

from config import LogConfig, app_configs

logger = logging.getLogger("root")


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    dictConfig(LogConfig().model_dump())
    yield


app = FastAPI(**app_configs, lifespan=lifespan)

@app.get("/")
async def root() -> dict:
    logger.warning("Hello from backend logger")
    return {"title": "Hello World"}
