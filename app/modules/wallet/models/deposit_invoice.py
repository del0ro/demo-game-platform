"""Модель инвойса на пополнение кошелька."""

from datetime import datetime

from sqlalchemy import BigInteger, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, MoneyType
from app.core.value_objects.money import Money
from app.modules.wallet.enums import DepositInvoiceStatusEnum


class DepositInvoiceModel(Base):
    """Запрошенный инвойс на депозит.

    Баланс зачисляется после перехода инвойса в статус `PAID`.
    """

    __tablename__ = "deposit_invoices"

    user_tg_id: Mapped[int] = mapped_column(BigInteger(), nullable=False, index=True)
    amount: Mapped[Money] = mapped_column(MoneyType(10, 4), nullable=False)
    provider_invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    status: Mapped[DepositInvoiceStatusEnum] = mapped_column(
        Enum(DepositInvoiceStatusEnum, native_enum=False, length=20),
        nullable=False,
        default=DepositInvoiceStatusEnum.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
