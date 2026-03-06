"""ORM-модель баланса пользователя."""

from datetime import datetime

from sqlalchemy import BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, MoneyType
from app.core.value_objects.money import Money


class BalanceModel(Base):
    """Текущий баланс кошелька пользователя."""

    __tablename__ = "wallet_balances"

    user_tg_id: Mapped[int] = mapped_column(
        BigInteger(),
        unique=True,
        nullable=False,
        index=True,
    )
    amount: Mapped[Money] = mapped_column(
        MoneyType(10, 4), nullable=False, default=Money("0.0")
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )
