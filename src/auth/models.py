import sqlalchemy as sqa
import sqlalchemy.orm as sqo
from uuid import uuid4

from src.database import Base # type: ignore
from src.auth import types # type: ignore


class User(Base):
    __tablename__ = "users"
    id: sqo.Mapped[types.UserId] = sqo.mapped_column(primary_key=True, autoincrement=True)
    email: sqo.Mapped[types.Email] = sqo.mapped_column(unique=True)
    rule: sqo.Mapped[str | None] = sqo.mapped_column(default="user")
    hashed_password: sqo.Mapped[str] = sqo.mapped_column()

    profile: sqo.Mapped["Profile"] = sqo.relationship(back_populates="user", cascade="all,delete-orphan")

    def __repr__(self) -> str:
        return f"user {self.id} {self.email}"


class Profile(Base):
    __tablename__ = "profiles"
    id: sqo.Mapped[types.ProfileId] = sqo.mapped_column(primary_key=True, default=uuid4)
    first_name: sqo.Mapped[str | None] = sqo.mapped_column(sqa.String(64))
    last_name: sqo.Mapped[str | None] = sqo.mapped_column(sqa.String(64))
    age: sqo.Mapped[int | None] = sqo.mapped_column()
    user_id: sqo.Mapped[types.UserId] = sqo.mapped_column(sqa.ForeignKey("users.id"), index=True)

    user: sqo.Mapped["User"] = sqo.relationship(back_populates="profile")

    def __repr__(self) -> str:
        return f"profile {self.id} {(self.last_name)}"
