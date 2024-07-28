import sqlalchemy as sqa
import sqlalchemy.orm as sqo

from src.database import Base # type: ignore
from src.auth import types # type: ignore


class User(Base):
    __tablename__ = "users"
    id: sqo.Mapped[types.UserId] = sqo.mapped_column(primary_key=True, autoincrement=True)
    email: sqo.Mapped[types.Email] = sqo.mapped_column(sqa.String(80), unique=True, index=True)
    rule: sqo.Mapped[str | None] = sqo.mapped_column(sqa.String(30), default="user")
    hashed_password: sqo.Mapped[str] = sqo.mapped_column()
    is_active: sqo.Mapped[bool] = sqo.mapped_column(default=False)

    def __repr__(self) -> str:
        return f"user {self.id} {self.email}"
