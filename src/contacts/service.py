import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import IntegrityError

from src.contacts import schemas
from src.pagination import SortEnum
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


async def get_my_contacts(
        *, creator_id: UserId, engine: AsyncEngine,
        per_page: int, page: int, order: SortEnum
) -> dict:
    order_by = sa.desc if order.value == "desc" else sa.asc
    offset = 0 if page == 1 else (page - 1) * per_page

    contacts_query = sa.select(Contact.name, Contact.phone_number, Contact.description).where(
        Contact.creator == creator_id
    ).limit(per_page).offset(offset).order_by(order_by(Contact.id))
    count_query = sa.select(sa.func.count()).select_from(sa.select(Contact.id).where(
        Contact.creator == creator_id
    ).subquery())

    async with engine.connect() as transaction:
        result: sa.CursorResult[tuple[str, str, str | None]] = (
            await transaction.execute(contacts_query)
        )
        count = await transaction.scalar(count_query)

    assert count is not None
    return {
        "count": count,
        "contacts": [
            {"name": contact.name , "phone_number": contact.phone_number, "description": contact.description}
            for contact in result.all()
        ]
    }



# async def get_contacts(
#         *,
#         pagination: Annotated[Pagination, Depends(pagination_dependency)],
#         db_connection: AsyncConnection
# ):
#     query = sqa.Select(Contact)
#     print(pagination())
