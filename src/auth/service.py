import sqlalchemy as sqa
from sqlalchemy.exc import IntegrityError

from src import database
from src.auth.types import Password
from src.auth.utils import get_password_hash, verify_password, encode_access_token
from src.auth.models import User
from src.auth.exceptions import EmailAlreadyExists, UserNotFound


async def register(*, email: str, password: Password) -> None:
    hashed_password = get_password_hash(password=password)
    query = sqa.insert(User).values(email=email, hashed_password=hashed_password)
    try:
        await database.execute(query=query, commit_after=True)
    except IntegrityError:
        raise EmailAlreadyExists


async def login(*, email: str, password: str):
    query = sqa.select(User).where(User.email == email)
    user = await database.fetch_one(query=query)
    if not user:
        raise UserNotFound
    if not verify_password(plain_password=password, hashed_password=user["hashed_password"]):
        raise UserNotFound
    return encode_access_token(user_id=user["id"], user_rule=user["rule"])
