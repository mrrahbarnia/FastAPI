import sqlalchemy as sa

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import IntegrityError
from fastapi import Depends

from src import database
# from src.pagination import pagination_dependency, Pagination
from src.contacts import exceptions
from src.contacts.models import Contact
from src.auth.types import UserId

async def create_contact(
        *, name: str, phone_number: str, description: str | None,
        creator_id: UserId, engine: AsyncEngine
) -> None:
    query = sa.Insert(Contact).values(
        {
            Contact.name: name,
            Contact.phone_number: phone_number,
            Contact.description: description,
            Contact.creator: creator_id
        }
    )
    try:
        async with engine.begin() as transaction:
            await transaction.execute(query)
    except IntegrityError:
        raise exceptions.PhoneNumberAlreadyExists


async def get_my_contacts(*, creator_id: UserId, engine: AsyncEngine) -> list[tuple[str, str, str | None]]:
    query = sa.select(Contact.name, Contact.phone_number, Contact.description).where(
        Contact.creator == creator_id
    )
    async with engine.connect() as transaction:
        result: sa.CursorResult[tuple[str, str, str | None]] = (
            await transaction.execute(query)
        )
    return ([r._tuple() for r in result.all()])



# async def get_contacts(
#         *,
#         pagination: Annotated[Pagination, Depends(pagination_dependency)],
#         db_connection: AsyncConnection
# ):
#     query = sqa.Select(Contact)
#     print(pagination())
