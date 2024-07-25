import jwt
from typing import Annotated, Literal
from jwt import exceptions

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from src.auth.exceptions import CredentialsException, IsAdminException
from src.auth.config import auth_config

secret_key = auth_config.SECRET_KEY
algorithm = auth_config.JWT_ALGORITHM

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")


def decode_access_token(token: Annotated[str, Depends(oauth2_schema)]):
    try:
        data = jwt.decode(jwt=token, key=secret_key, algorithms=[algorithm])
    except exceptions.ExpiredSignatureError:
        raise
    except exceptions.InvalidTokenError:
        raise CredentialsException
    return data


def get_current_user_id(data: Annotated[dict, Depends(decode_access_token)]) -> int:
    if "user_id" not in data:
        raise CredentialsException
    return data["user_id"]


def is_admin(data: Annotated[dict, Depends(decode_access_token)]) -> Literal[True]:
    if "user_rule" not in data:
        raise CredentialsException
    if data["user_rule"] != "admin":
        raise IsAdminException
    return True
