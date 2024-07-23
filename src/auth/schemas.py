from pydantic import BaseModel, ConfigDict, EmailStr, model_validator, Field


class RegisterIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    email: EmailStr
    password: str
    confirm_password: str = Field(alias="confirmPassword")

    @model_validator(mode="after")
    @classmethod
    def validate_passwords(self):
        password = self.password
        confirm_password = self.confirm_password

        if password is not None and confirm_password is not None and password != confirm_password:
            raise ValueError("Passwords do not match")
        return self


# class RegisterOut(BaseModel):

