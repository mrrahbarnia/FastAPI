# from enum import Enum
# from typing import Annotated
# from pydantic import Field
# from fastapi import Query

# from src.schemas import CustomBaseModel


# class OrderEnum(Enum):
#     DESC = "desc"
#     ASC = "asc"


# class Pagination(CustomBaseModel):
#     per_page: int | None = Field(alias="perPage", default=10)
#     page: int | None = 1
#     order: OrderEnum


# async def pagination_dependency(
#         order: Annotated[OrderEnum, Query()] = OrderEnum.DESC,
#         page: Annotated[int | None, Query(ge=1)] = 1,
#         per_page: Annotated[int | None, Query(ge=1)] = 10,
# ) -> Pagination:
#     """
#     General pagination model for using in all application.
#     """
#     return Pagination(perPage=per_page, page=page, order=order)

