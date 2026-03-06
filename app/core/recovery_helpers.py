"""Вспомогательные функции для восстановительной проверки при старте."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.game.enums import GameSessionStatus
from app.modules.game.models import GameSessionModel
from app.modules.wallet.enums import DepositInvoiceStatusEnum
from app.modules.wallet.models import DepositInvoiceModel


async def get_pending_deposit_ids(session: AsyncSession) -> list[int]:
    """Возвращает список ID депозитов в статусе `PENDING`."""
    stmt = select(DepositInvoiceModel.id).where(
        DepositInvoiceModel.status == DepositInvoiceStatusEnum.PENDING
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_active_game_session_ids(session: AsyncSession) -> list[int]:
    """Возвращает список ID активных или ожидающих игровых сессий."""
    stmt = select(GameSessionModel.id).where(
        GameSessionModel.status.in_(
            [GameSessionStatus.PENDING_START, GameSessionStatus.ACTIVE]
        )
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
