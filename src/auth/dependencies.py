import jwt
from typing import Annotated, Literal
from jwt import exceptions as jwt_exceptions

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.auth import exceptions
from src.auth import service
from src.auth.config import auth_config
from src.auth.models import User


secret_key = auth_config.SECRET_KEY
algorithm = auth_config.JWT_ALGORITHM

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")


async def decode_access_token(token: Annotated[str, Depends(oauth2_schema)]) -> dict:
    try:
        data = jwt.decode(jwt=token, key=secret_key, algorithms=[algorithm])
    except jwt_exceptions.ExpiredSignatureError:
        raise
    except jwt_exceptions.InvalidTokenError:
        raise exceptions.CredentialsException
    return data


async def get_current_active_user(data: Annotated[dict, Depends(decode_access_token)]) -> User:
    if "user_id" not in data:
        raise exceptions.CredentialsException
    user_id = data["user_id"]
    user = await service.get_user_by_id(user_id)
    if user["is_active"] is False:
        raise exceptions.NotActiveUser
    return user


async def is_admin(data: Annotated[dict, Depends(decode_access_token)]) -> Literal[True]:
    if "user_rule" not in data:
        raise exceptions.CredentialsException
    if data["user_rule"] != "admin":
        raise exceptions.IsAdminException
    return True
