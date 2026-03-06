"""ORM-модель пользователя с базовым доменным поведением."""

from datetime import datetime

from sqlalchemy import BigInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.value_objects.money import Money


class UserModel(Base):
    """Пользователь demo-приложения."""

    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(BigInteger(), unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    def update_from_telegram(
        self,
        name: str | None,
        username: str | None,
    ) -> None:
        self.name = name
        self.username = username
