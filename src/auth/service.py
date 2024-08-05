import asyncio
import logging
import sqlalchemy as sa

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from src.database import get_redis_connection
from src.auth import exceptions
from src.auth import utils
from src.auth.config import auth_config
from src.auth.types import Password, UserId, Email
from src.auth.models import User

logger = logging.getLogger("auth")


async def send_email(email: str, subject: str):
    # TODO: Sending email
    await asyncio.sleep(5)
    logger.info(f"Sending {subject} to {email}...")


async def get_user_by_id(id: UserId, engine: AsyncEngine):
    query = sa.select(User).where(User.id == id)
    async with engine.begin() as transaction:
        user = (await transaction.execute(query)).first()
    if not user:
        raise exceptions.UserNotFound
    
    return user._tuple()


async def register(
        *, email: Email, password: Password, verification_code: str, engine: AsyncEngine
) -> None:
    hashed_password = utils.get_password_hash(password=password)
    query = sa.insert(User).values(
        {
            User.email: email,
            User.hashed_password: hashed_password
        }
    )
    try:
        async with engine.begin() as transaction:
            await transaction.execute(query)

        get_redis_connection().set(
            name=f"verification_code:{verification_code}",
            value=email,
            ex=auth_config.VERIFICATION_CODE_LIFE_TIME_SECONDS
        )  
    except IntegrityError:
        raise exceptions.EmailAlreadyExists


async def login(*, email: str, password: str, engine: AsyncEngine) -> str:
    query = sa.select(User).where(User.email == email)
    async with engine.begin() as transaction:
        user: sa.Row[tuple[User]] | None = (await transaction.execute(query)).first()
    if not user:
        raise exceptions.UserNotFound
    if not utils.verify_password(
        plain_password=password, hashed_password=user.hashed_password
    ):
        raise exceptions.UserNotFound
    if user.is_active is False:
        raise exceptions.NotActiveUser

    return utils.encode_access_token(user_id=user.id, user_rule=user.rule)


async def verify_account(*, verification_code: str, engine: AsyncEngine) -> None:
    email = get_redis_connection().get(
        name=f"verification_code:{verification_code}"
    )
    if not email:
        raise exceptions.InvalidVerificationCode
    query = sa.update(User).where(User.email==email).values({User.is_active: True})
    async with engine.begin() as transaction:
        await transaction.execute(query)


async def change_password(
        *, user: User, old_password: Password, new_password: Password, engine: AsyncEngine
) -> None: 
    if not utils.verify_password(
        plain_password=str(old_password), hashed_password=user.hashed_password
    ):
        raise exceptions.WrongOldPassword
    new_hashed_password = utils.get_password_hash(new_password)
    query = sa.update(User).where(User.hashed_password==user.hashed_password).values(
        {
            User.hashed_password: new_hashed_password
        }
    )
    async with engine.begin() as transaction:
        await transaction.execute(query)
