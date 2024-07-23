import logging

from fastapi import APIRouter

router = APIRouter()

logger = logging.getLogger("root")


@router.get("/")
async def register() -> dict:
    return {"Root": True}
