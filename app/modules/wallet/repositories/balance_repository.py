"""Репозиторий баланса пользователя по `user_tg_id`."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.value_objects.money import Money
from app.modules.wallet.models.balance import BalanceModel


class BalanceRepository:
    """Получает, создаёт и сохраняет баланс пользователя."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_tg_id(self, user_tg_id: int) -> BalanceModel | None:
        stmt = select(BalanceModel).where(BalanceModel.user_tg_id == user_tg_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        user_tg_id: int,
        default_amount: Money | None = None,
    ) -> BalanceModel:
        balance = await self.get_by_user_tg_id(user_tg_id)
        if balance is not None:
            return balance
        balance = BalanceModel(
            user_tg_id=user_tg_id,
            amount=default_amount if default_amount is not None else Money("0"),
        )
        self._session.add(balance)
        await self._session.flush()
        await self._session.refresh(balance)
        return balance

    async def save(self, balance: BalanceModel) -> None:
        await self._session.flush()
