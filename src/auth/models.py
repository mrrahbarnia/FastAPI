import sqlalchemy as sa
import sqlalchemy.orm as so

from datetime import datetime

from src.database import Base
from src.auth import types


class User(Base):
    __tablename__ = "users"
    id: so.Mapped[types.UserId] = so.mapped_column(primary_key=True, autoincrement=True)
    email: so.Mapped[types.Email] = so.mapped_column(sa.String(80), unique=True, index=True)
    rule: so.Mapped[str | None] = so.mapped_column(sa.String(30), default="user")
    hashed_password: so.Mapped[str] = so.mapped_column()
    is_active: so.Mapped[bool] = so.mapped_column(default=False)
    created_at: so.Mapped[datetime] = so.mapped_column(default=sa.func.now())

    def __repr__(self) -> str:
        return f"User {self.id} {self.email}"
