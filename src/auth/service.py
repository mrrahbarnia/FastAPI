import asyncio
import logging
import sqlalchemy as sqa

from typing import Mapping
from sqlalchemy.exc import IntegrityError

from src import database
from src.auth import exceptions
from src.auth import utils
from src.auth.config import auth_config
from src.auth.types import Password, UserId
from src.auth.models import User, Profile

logger = logging.getLogger("auth")


async def send_email(email: str, subject: str):
    # TODO: Sending email
    await asyncio.sleep(5)
    logger.info(f"Sending {subject} to {email}...")


async def get_user_by_id(id: UserId) -> Mapping:
    query = sqa.select(User).where(User.id == id)
    user = await database.fetch_one(query=query)
    if not user:
        raise exceptions.UserNotFound
    return user


async def register(*, email: str, password: Password, verification_code: str) -> None:
    hashed_password = utils.get_password_hash(password=password)
    user_query = sqa.insert(User).values(email=email, hashed_password=hashed_password)
    try:
        await database.execute(query=user_query, commit_after=True)
        database.get_redis_connection().set(
            name=f"verification_code:{verification_code}",
            value=email,
            ex=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    except IntegrityError:
        raise exceptions.EmailAlreadyExists


async def login(*, email: str, password: str) -> str:
    query = sqa.select(User).where(User.email == email)
    user = await database.fetch_one(query=query)
    if not user:
        raise exceptions.UserNotFound
    if not utils.verify_password(
        plain_password=password, hashed_password=user["hashed_password"]
    ):
        raise exceptions.UserNotFound
    if user["is_active"] is False:
        raise exceptions.NotActiveUser

    return utils.encode_access_token(user_id=user["id"], user_rule=user["rule"])


async def verify_account(*, verification_code):
    email = database.get_redis_connection().get(
        name=f"verification_code:{verification_code}"
    )
    if not email:
        raise exceptions.InvalidVerificationCode
    query = sqa.update(User).where(User.email == email).values(is_active=True)
    await database.execute(query=query, commit_after=True)


async def set_profile(
        *,
        user_id: int,
        first_name: str | None,
        last_name: str | None,
        age: int | None
):
    query = sqa.update(Profile).where(Profile.user_id == user_id).values(
        first_name=first_name, last_name=last_name, age=age, user_id=user_id
    )
    await database.execute(query=query, commit_after=True)


async def get_profile(*, user_id: UserId):
    query = sqa.select(Profile).where(Profile.user_id == user_id)
    profile = await database.fetch_one(query=query)
    return profile
