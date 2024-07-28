import re

from pydantic import (
    BaseModel, ConfigDict, EmailStr, model_validator, Field, field_validator
)

from src.schemas import CustomBaseModel
from src.auth.config import auth_config
from src.auth.types import Password

PASSWORD_PATTERN = auth_config.PASSWORD_PATTERN


class RegisterOut(CustomBaseModel):
    email: EmailStr


class RegisterIn(RegisterOut):
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {   
                "email": "user@example.com",
                "password": "mM@#12345678n",
                "confirmPassword": "mM@#12345678n",
            }
        ]
    })
    password: Password
    confirm_password: Password = Field(alias="confirmPassword")

    @field_validator("password", mode="after")
    @classmethod
    def validate_password_pattern(cls, password: Password) -> Password:
        if not re.match(PASSWORD_PATTERN, password):
            raise ValueError(
                "Has minimum 8 characters in length",
                "At least one uppercase English letter",
                "At least one lowercase English letter",
                "At least one digit",
                "At least one special character"
            )
        return password

    @model_validator(mode="after")
    def validate_passwords(self):
        password = self.password
        confirm_password = self.confirm_password

        if password is not None and confirm_password is not None and password != confirm_password:
            raise ValueError("Passwords don't match!")
        return self


class LoginIn(BaseModel):
    username: str
    password: Password


class LoginOut(BaseModel):
    email: str
    access_token: str
    token_type: str


class VerificationIn(CustomBaseModel):
    verification_code: str = Field(alias="verificationCode")


class ChangePasswordIn(CustomBaseModel):
    old_password: Password = Field(alias="oldPassword")
    new_password: Password = Field(alias="newPassword")
    confirm_password: Password = Field(alias="confirmPassword")

    @field_validator("new_password", mode="after")
    @classmethod
    def validate_password_pattern(cls, new_password: Password) -> Password:
        if not re.match(PASSWORD_PATTERN, new_password):
            raise ValueError(
                "Has minimum 8 characters in length",
                "At least one uppercase English letter",
                "At least one lowercase English letter",
                "At least one digit",
                "At least one special character"
            )
        return new_password

    @model_validator(mode="after")
    def validate_passwords(self):
        new_password = self.new_password
        confirm_password = self.confirm_password
        if new_password is not None and confirm_password is not None and new_password != confirm_password:
            raise ValueError("Passwords don't match!")
        return self