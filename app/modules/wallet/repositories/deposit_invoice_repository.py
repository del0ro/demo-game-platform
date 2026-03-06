"""Репозиторий инвойсов на депозит."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.wallet.models.deposit_invoice import DepositInvoiceModel


class DepositInvoiceRepository:
    """Создаёт и ищет инвойсы на пополнение кошелька."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, invoice: DepositInvoiceModel) -> DepositInvoiceModel:
        self._session.add(invoice)
        await self._session.flush()
        await self._session.refresh(invoice)
        return invoice

    async def get_by_id(self, invoice_id: int) -> DepositInvoiceModel | None:
        return await self._session.get(DepositInvoiceModel, invoice_id)

    async def get_by_id_for_update(
        self, invoice_id: int
    ) -> DepositInvoiceModel | None:
        stmt = (
            select(DepositInvoiceModel)
            .where(DepositInvoiceModel.id == invoice_id)
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_provider_invoice_id(
        self, provider_invoice_id: str
    ) -> DepositInvoiceModel | None:
        stmt = select(DepositInvoiceModel).where(
            DepositInvoiceModel.provider_invoice_id == provider_invoice_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_provider_invoice_id_for_update(
        self, provider_invoice_id: str
    ) -> DepositInvoiceModel | None:
        stmt = (
            select(DepositInvoiceModel)
            .where(DepositInvoiceModel.provider_invoice_id == provider_invoice_id)
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, invoice: DepositInvoiceModel) -> None:
        await self._session.flush()
