"""Перечисления модуля game."""

import enum


class GameType(str, enum.Enum):
    """Тип игры."""

    HILO = "hilo"
    DICE = "dice"


class GameSessionStatus(str, enum.Enum):
    """Универсальный статус игровой сессии для разных типов игр."""

    PENDING_START = "pending_start"  # waiting for first action
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"
