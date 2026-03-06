"""Startup recovery для demo-приложения.

При старте модуль выполняет диагностическую проверку незавершённых операций и
пишет результат в лог. Это не полноценный reconciliation flow, а прозрачная
точка расширения для production-версии.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger
from app.core.recovery_helpers import (
    get_active_game_session_ids,
    get_pending_deposit_ids,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker as AsyncSessionMaker

logger = get_logger(__name__)


async def run_startup_recovery(sessionmaker: "AsyncSessionMaker[AsyncSession]") -> None:
    """Логирует pending депозиты и незавершённые игровые сессии."""
    async with sessionmaker() as session:
        async with session.begin():
            pending_deposits = await get_pending_deposit_ids(session)
            if pending_deposits:
                logger.info(
                    "Startup recovery: найдено pending депозитов: %s",
                    pending_deposits,
                )

            active_sessions = await get_active_game_session_ids(session)
            if active_sessions:
                logger.info(
                    "Startup recovery: найдено активных/ожидающих игр: %s",
                    active_sessions,
                )

            if not pending_deposits and not active_sessions:
                logger.debug("Startup recovery: незавершённых операций не найдено")
