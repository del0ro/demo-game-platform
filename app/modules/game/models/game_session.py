"""ORM-модель игровой сессии с общими полями для всех типов игр."""

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, MoneyType
from app.core.value_objects.money import Money
from app.modules.game.enums import GameSessionStatus, GameType


class GameSessionModel(Base):
    """Игровая сессия с полями, общими для любого типа игры."""

    __tablename__ = "game_sessions"

    user_tg_id: Mapped[int] = mapped_column(BigInteger(), nullable=False, index=True)
    game_type: Mapped[GameType] = mapped_column(
        Enum(GameType, native_enum=False, length=20),
        nullable=False,
    )
    bet_amount: Mapped[Money] = mapped_column(MoneyType(10, 2), nullable=False)
    last_message_id: Mapped[int | None] = mapped_column(BigInteger(), nullable=True)
    status: Mapped[GameSessionStatus] = mapped_column(
        Enum(GameSessionStatus, native_enum=False, length=20),
        nullable=False,
        default=GameSessionStatus.PENDING_START,
    )
    win_amount: Mapped[Money] = mapped_column(
        MoneyType(10, 2),
        nullable=False,
        default=Money("0.0"),
    )
    is_win: Mapped[bool | None] = mapped_column(nullable=True)
    is_bonus: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)

    @property
    def is_finished(self) -> bool:
        return self.status in (
            GameSessionStatus.WON,
            GameSessionStatus.LOST,
            GameSessionStatus.CANCELLED,
        )

    def activate(self) -> None:
        if self.status != GameSessionStatus.PENDING_START:
            raise ValueError(f"Cannot activate game session with status: {self.status}")
        self.status = GameSessionStatus.ACTIVE

    def set_result(self, won: bool, win_amount: Money) -> None:
        self.is_win = won
        self.win_amount = win_amount
        self.status = GameSessionStatus.WON if won else GameSessionStatus.LOST
        self.finished_at = datetime.now(timezone.utc).replace(tzinfo=None)

    def cancel(self) -> None:
        if self.status == GameSessionStatus.PENDING_START:
            self.status = GameSessionStatus.CANCELLED
            self.finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            raise ValueError(f"Cannot cancel game session in status {self.status}")

    def update_bet_amount(self, bet_amount: Money) -> None:
        if bet_amount.amount < 0:
            raise ValueError("Bet amount must be greater than or equal to 0")
        self.bet_amount = bet_amount

    def update_last_message_id(self, message_id: int) -> None:
        self.last_message_id = message_id