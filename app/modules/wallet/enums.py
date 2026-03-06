"""Перечисления, используемые в модуле wallet."""

from enum import Enum


class TransactionTypeEnum(str, Enum):
    """Направление движения денег в транзакции."""

    DEBIT = "debit"
    CREDIT = "credit"


class TransactionReasonEnum(str, Enum):
    """Причина появления транзакции в кошельке."""

    DEPOSIT = "deposit"
    WITHDRAW_CHECK = "withdraw_check"
    WITHDRAW_TRANSFER = "withdraw_transfer"
    GAME_LOSS = "game_loss"
    GAME_WIN = "game_win"
    BONUS_GAME_WIN = "bonus_game_win"
    REFERRAL = "referral"
    BONUS = "bonus"  # league / daily bonuses
    CASHBACK = "cashback"
    BET = "bet"


class DepositInvoiceStatusEnum(str, Enum):
    """Статус инвойса на депозит."""

    PENDING = "pending"
    PAID = "paid"
    EXPIRED = "expired"

