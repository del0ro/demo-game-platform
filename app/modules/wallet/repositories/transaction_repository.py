"""Репозиторий транзакций кошелька."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.value_objects.money import Money
from app.modules.wallet.enums import TransactionReasonEnum, TransactionTypeEnum
from app.modules.wallet.models.transaction import TransactionModel


class TransactionRepository:
    """Создаёт транзакции и возвращает историю операций."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        user_tg_id: int,
        amount: Money,
        type_: TransactionTypeEnum,
        reason: TransactionReasonEnum,
        external_id: str | None = None,
    ) -> TransactionModel:
        tx = TransactionModel(
            user_tg_id=user_tg_id,
            amount=amount,
            type=type_,
            reason=reason,
            external_id=external_id or str(uuid.uuid4()),
        )
        self._session.add(tx)
        await self._session.flush()
        await self._session.refresh(tx)
        return tx

    async def list_recent_by_user(
        self,
        user_tg_id: int,
        limit: int = 20,
    ) -> tuple[TransactionModel, ...]:
        stmt = (
            select(TransactionModel)
            .where(TransactionModel.user_tg_id == user_tg_id)
            .order_by(TransactionModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return tuple(result.scalars().all())
