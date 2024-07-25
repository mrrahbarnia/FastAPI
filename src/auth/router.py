import logging

from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, status, Depends

from src.auth.dependencies import get_current_user_id
from src.auth import schemas
from src.auth import service

router = APIRouter()

logger = logging.getLogger("root")


@router.post(
        "/register/",
        response_model=schemas.RegisterOut,
        status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: schemas.RegisterIn,

) -> schemas.RegisterOut:
    await service.register(email=user_data.email, password=user_data.password)
    return schemas.RegisterOut(email=user_data.email)


@router.post(
    "/login/",
    response_model=schemas.LoginOut,
    status_code=status.HTTP_200_OK
)
async def login(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> schemas.LoginOut:
    access_token = await service.login(email=user_data.username, password=user_data.password)
    return schemas.LoginOut(email=user_data.username, access_token=access_token, token_type="bearer")


@router.get(
    "/my-profile/",
    status_code=status.HTTP_200_OK
)
async def get_my_profile(
    id: int = Depends(get_current_user_id)
):
    return id