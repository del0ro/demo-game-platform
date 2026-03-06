"""Детали игры HiLo: одна запись на шаг или бросок."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, MoneyType
from app.core.value_objects.money import Money


class GameHiloDetailsModel(Base):
    """Один шаг HiLo, связанный с игровой сессией."""

    __tablename__ = "game_hilo_details"

    game_session_id: Mapped[int] = mapped_column(
        ForeignKey("game_sessions.id"),
        nullable=False,
        index=True,
    )
    first_dice_value: Mapped[int] = mapped_column(nullable=False)
    second_dice_value: Mapped[int] = mapped_column(nullable=False)
    roll_number: Mapped[int] = mapped_column(nullable=False, default=1)
    chosen_outcome: Mapped[str | None] = mapped_column(String(10), nullable=True)
    multiplier: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("1.0"),
    )
    cumulative_multiplier: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("1.0"),
    )
    win_amount: Mapped[Money] = mapped_column(
        MoneyType(10, 2),
        nullable=False,
        default=Money(0),
    )
    is_win: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
