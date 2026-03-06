"""ORM-модель пользовательских игровых настроек."""

from datetime import datetime

from sqlalchemy import BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, MoneyType
from app.core.value_objects.money import Money


class GameSettingsModel(Base):
    """Настройки игры для конкретного пользователя."""

    __tablename__ = "game_settings"

    user_tg_id: Mapped[int] = mapped_column(
        BigInteger(),
        nullable=False,
        unique=True,
        index=True,
    )
    bet_amount: Mapped[Money] = mapped_column(
        MoneyType(10, 2),
        nullable=False,
        default=Money("0.1"),
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def update_bet_amount(self, bet_amount: Money) -> None:
        if bet_amount.amount < 0:
            raise ValueError("Bet amount must be greater than or equal to 0")
        self.bet_amount = bet_amount
