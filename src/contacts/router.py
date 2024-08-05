from typing import Annotated, Any
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncEngine

# from src.pagination import pagination_dependency, Pagination
from src.database import get_engine
from src.contacts import schemas
from src.contacts import service
from src.auth.models import User
from src.auth.dependencies import get_current_active_user

router = APIRouter()

@router.post(
        "/create/",
        status_code=status.HTTP_201_CREATED,
        # response_model=schemas.Contact
)
async def add_contact(
    input_data: schemas.Contact,
    active_user: Annotated[User, Depends(get_current_active_user)],
    engine: Annotated[AsyncEngine, Depends(get_engine)]
):
    await service.create_contact(
        name=input_data.name,
        phone_number=input_data.phone_number,
        description=input_data.description,
        creator_id=active_user.id,
        engine=engine
    )
    return input_data


@router.get("/my-contacts/", response_model=list[schemas.Contact])
async def get_my_contacts(
    active_user: Annotated[User, Depends(get_current_active_user)],
    engine: Annotated[AsyncEngine, Depends(get_engine)]
) -> Any:
    contacts = await service.get_my_contacts(creator_id=active_user.id, engine=engine)
    return contacts



# @router.get("/all-contacts/", status_code=status.HTTP_200_OK)
# async def get_contacts(
#     active_user: Annotated[dict, Depends(get_current_active_user)],
#     db_connection: Annotated[AsyncConnection, Depends(get_db_connection)],
#     pagination: Annotated[Pagination, Depends(pagination_dependency)],
# ):
#     print(pagination.model_dump())
#     await service.get_contacts()