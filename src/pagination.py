from typing import Annotated
from enum import Enum
from pydantic import Field
from fastapi import Query

from src.schemas import CustomBaseModel


class SortEnum(Enum):
    ASC = "asc"
    DESC = "desc"


class Pagination(CustomBaseModel):
    per_page: int = Field(serialization_alias="perPage")
    page: int
    order: SortEnum


async def pagination_params(
        page: Annotated[int, Query()] = 1,
        per_page: Annotated[int, Query()] = 10,
        order: SortEnum = SortEnum.DESC
):
    return Pagination(per_page=per_page, page=page, order=order)