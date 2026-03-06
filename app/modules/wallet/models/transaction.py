"""ORM-модель транзакции кошелька."""

from datetime import datetime

from sqlalchemy import BigInteger, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, MoneyType
from app.core.value_objects.money import Money
from app.modules.wallet.enums import TransactionReasonEnum, TransactionTypeEnum


class TransactionModel(Base):
    """Операция по кошельку: зачисление или списание."""

    __tablename__ = "transactions"

    user_tg_id: Mapped[int] = mapped_column(BigInteger(), nullable=False, index=True)
    amount: Mapped[Money] = mapped_column(MoneyType(10, 4), nullable=False)
    type: Mapped[TransactionTypeEnum] = mapped_column(
        Enum(TransactionTypeEnum, native_enum=False, length=10),
        nullable=False,
    )
    reason: Mapped[TransactionReasonEnum] = mapped_column(
        Enum(TransactionReasonEnum, native_enum=False, length=30),
        nullable=False,
    )
    external_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
