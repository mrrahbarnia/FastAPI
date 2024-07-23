from pydantic import BaseModel, ConfigDict


class CustomModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, extra="forbid"
    )