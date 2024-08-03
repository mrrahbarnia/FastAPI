import logging

from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, status, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncConnection

from src.database import get_db_connection
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
    input_data: schemas.RegisterIn, worker: BackgroundTasks, 
    db_connection: Annotated[AsyncConnection, Depends(get_db_connection)]
) -> schemas.RegisterOut:
    verification_code = generate_random_code()
    await service.register(
        email=input_data.email, password=input_data.password,
        verification_code=verification_code,
        db_connection=db_connection
    )
    worker.add_task(service.send_email, input_data.email, verification_code)
    return schemas.RegisterOut(email=input_data.email)


@router.post(
    "/login/",
    response_model=schemas.LoginOut,
    status_code=status.HTTP_200_OK
)
async def login(
    input_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_connection: Annotated[AsyncConnection, Depends(get_db_connection)]
) -> schemas.LoginOut:
    access_token = await service.login(
        email=input_data.username, password=input_data.password, db_connection=db_connection
    )
    return schemas.LoginOut(email=input_data.username, access_token=access_token, token_type="bearer")


@router.post("/verify-account/", status_code=status.HTTP_200_OK)
async def verify_account(
    input_data: schemas.VerificationIn,
    db_connection: Annotated[AsyncConnection, Depends(get_db_connection)]
) -> dict:
    await service.verify_account(verification_code=input_data.verification_code, db_connection=db_connection)
    return {"message": "Account verified successfully"}

@router.put("/change-password/", status_code=status.HTTP_200_OK)
async def change_password(
    input_data: schemas.ChangePasswordIn,
    active_user: Annotated[dict, Depends(get_current_active_user)],
    db_connection: Annotated[AsyncConnection, Depends(get_db_connection)]
) -> dict:
    await service.change_password(
        user=active_user, old_password=input_data.old_password, new_password=input_data.new_password, db_connection=db_connection
    )
    return {"message": "Password changed successfully"}
    
    