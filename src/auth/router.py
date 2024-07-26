import logging

from typing import Annotated, Mapping
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, status, Depends, BackgroundTasks

from src.auth import schemas
from src.auth import service
from src.auth.dependencies import get_current_active_user
from src.auth.utils import generate_random_code

router = APIRouter()

logger = logging.getLogger("root")


@router.post(
        "/register/",
        response_model=schemas.RegisterOut,
        status_code=status.HTTP_201_CREATED
)
async def register(
    input_data: schemas.RegisterIn, worker: BackgroundTasks
) -> schemas.RegisterOut:
    verification_code = generate_random_code()
    await service.register(
        email=input_data.email, password=input_data.password,
        verification_code=verification_code
    )
    worker.add_task(service.send_email, input_data.email, verification_code)
    return schemas.RegisterOut(email=input_data.email)


@router.post(
    "/login/",
    response_model=schemas.LoginOut,
    status_code=status.HTTP_200_OK
)
async def login(
    input_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> schemas.LoginOut:
    access_token = await service.login(email=input_data.username, password=input_data.password)
    return schemas.LoginOut(email=input_data.username, access_token=access_token, token_type="bearer")


@router.post("/verify-account/", status_code=status.HTTP_200_OK)
async def verify_account(input_data: schemas.VerificationIn) -> dict:
    await service.verify_account(verification_code=input_data.verification_code)
    return {"message": "Account verified successfully"}


@router.post(
    "/profile/set/",
    response_model=schemas.Profile,
    status_code=status.HTTP_201_CREATED
)
async def set_my_profile(
    input_data: schemas.Profile,
    current_user: Annotated[Mapping, Depends(get_current_active_user)]
) -> schemas.Profile:
    await service.set_profile(
        user_id=current_user["id"], first_name=input_data.first_name,
        last_name=input_data.last_name, age=input_data.age
    )
    return input_data


@router.get(
    "/profile/get/",
    response_model=schemas.Profile,
    status_code=status.HTTP_200_OK
)
async def get_my_profile(
    current_user: Annotated[Mapping, Depends(get_current_active_user)]
) -> schemas.Profile:
    profile = await service.get_profile(user_id=current_user["id"])
    return profile
