"""Запрос счёта на депозит через demo-провайдера."""

from dataclasses import dataclass

from app.core.value_objects.money import Money
from app.modules.wallet.enums import DepositInvoiceStatusEnum
from app.modules.wallet.models import DepositInvoiceModel
from app.modules.wallet.providers import DemoPaymentProvider
from app.modules.wallet.repositories import DepositInvoiceRepository


class RequestDepositInvoiceError(Exception):
    """Ошибка запроса счёта на депозит."""

    pass


@dataclass(slots=True, frozen=True)
class RequestedDepositInvoice:
    """Результат создания счёта на депозит."""

    invoice_id: int
    payment_url: str
    provider_invoice_id: str


async def request_deposit_invoice(
    deposit_invoice_repo: DepositInvoiceRepository,
    user_tg_id: int,
    amount: Money,
    provider: DemoPaymentProvider,
) -> RequestedDepositInvoice:
    """Создаёт счёт на депозит и возвращает данные для оплаты."""
    if amount.amount <= 0:
        raise RequestDepositInvoiceError("Amount must be positive")

    invoice = DepositInvoiceModel(
        user_tg_id=user_tg_id,
        amount=amount,
        status=DepositInvoiceStatusEnum.PENDING,
    )
    invoice = await deposit_invoice_repo.create(invoice)
    url, provider_id = provider.create_invoice(amount, user_tg_id)
    invoice.provider_invoice_id = provider_id
    await deposit_invoice_repo.save(invoice)

    return RequestedDepositInvoice(
        invoice_id=invoice.id,
        payment_url=url,
        provider_invoice_id=provider_id,
    )
