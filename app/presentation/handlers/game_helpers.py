"""Вспомогательные функции для игровых обработчиков."""

from __future__ import annotations

from typing import TypedDict

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.value_objects.money import Money
from app.modules.game.repositories import GameSessionRepository, GameSettingsRepository
from app.modules.wallet.repositories import BalanceRepository, TransactionRepository

logger = get_logger(__name__)


class GameRepositories(TypedDict):
    """Набор репозиториев для игровых обработчиков."""

    game_session_repo: GameSessionRepository
    game_settings_repo: GameSettingsRepository
    balance_repo: BalanceRepository
    transaction_repo: TransactionRepository


def get_game_repositories(session: AsyncSession) -> GameRepositories:
    """Собирает репозитории для игровых сценариев."""
    return {
        "game_session_repo": GameSessionRepository(session),
        "game_settings_repo": GameSettingsRepository(session),
        "balance_repo": BalanceRepository(session),
        "transaction_repo": TransactionRepository(session),
    }


def parse_money_argument(message: Message) -> Money | None:
    """Парсит сумму из команды вида `/command <amount>`."""
    if message.text is None:
        return None
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    try:
        return Money(parts[1].strip())
    except ValueError:
        return None


def build_start_game_text(bet_amount: Money) -> str:
    """Форматирует ответ после старта игры."""
    return (
        f"🎮 <b>Игра начата.</b>\n\n"
        f"<blockquote>💰 Ставка: ${bet_amount}</blockquote>\n\n"
        "Дальше можно:\n"
        "• `/bet <сумма>` — сделать ставку\n"
        "• `/finish_win [сумма]` — завершить игру выигрышем\n"
        "• `/finish_lose` — завершить игру проигрышем"
    )


def build_finish_game_text(won: bool, win_amount: Money) -> str:
    """Форматирует сообщение о завершении игры."""
    if won:
        return (
            "✅ <b>Игра завершена победой.</b>\n\n"
            f"<blockquote>🏆 Выигрыш: ${win_amount}</blockquote>"
        )
    return "❌ <b>Игра завершена.</b>\n\n<blockquote>Вы проиграли.</blockquote>"


def log_game_action(message: Message, action: str) -> None:
    """Логирует игровое действие пользователя."""
    if message.from_user is None:
        return
    logger.info(
        "%s | %s (%s)",
        action,
        message.from_user.full_name,
        message.from_user.id,
    )
