import sqlalchemy as sa
import sqlalchemy.orm as so

from datetime import datetime, UTC
from uuid import uuid4

from src.database import Base
from src.auth.types import UserId
from src.contacts.types import ContactId

class Contact(Base):
    __tablename__ = "contacts"
    id: so.Mapped[ContactId] = so.mapped_column(primary_key=True, default=uuid4)
    name: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    phone_number: so.Mapped[str] = so.mapped_column(sa.String(12), unique=True)
    description: so.Mapped[str | None] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(default=sa.func.now())
    updated_at: so.Mapped[datetime] = so.mapped_column(
        default=sa.func.now(), onupdate=sa.func.now()
    )

    creator: so.Mapped[UserId | None] = so.mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))

    def __repr__(self) -> str:
        return f"Contact {self.id} {self.name}"
