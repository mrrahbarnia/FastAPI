from pydantic import Field, field_validator, ConfigDict

from src.schemas import CustomBaseModel

class Contact(CustomBaseModel):
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {   
                "name": "John Doe",
                "phoneNumber": "09131234567",
                "description": "This is my best friend.",
            }
        ]
    })
    name: str = Field(max_length=120)
    phone_number: str = Field(alias="phoneNumber")
    description: str | None

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if len(value) != 11:
            raise ValueError("Phone number must be exact 11 digits.")
        return value