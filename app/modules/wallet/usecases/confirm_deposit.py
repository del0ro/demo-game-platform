"""Подтверждение депозита: блокировка счёта, проверка доступа, зачисление средств."""

import logging

from app.modules.wallet.enums import (
    DepositInvoiceStatusEnum,
    TransactionReasonEnum,
    TransactionTypeEnum,
)
from app.modules.wallet.repositories import (
    BalanceRepository,
    DepositInvoiceRepository,
    TransactionRepository,
)


class ConfirmDepositError(Exception):
    """Ошибка подтверждения депозита."""

    pass


logger = logging.getLogger(__name__)


async def confirm_deposit(
    deposit_repo: DepositInvoiceRepository,
    balance_repo: BalanceRepository,
    transaction_repo: TransactionRepository,
    actor_user_tg_id: int,
    allow_admin_override: bool = False,
    invoice_id: int | None = None,
    provider_invoice_id: str | None = None,
) -> bool:
    """Подтверждает счёт, если он принадлежит пользователю или администратору.

    Возвращает `True`, если произошло реальное зачисление, и `False`, если счёт
    уже был отмечен как оплаченный.
    """
    if invoice_id is not None:
        invoice = await deposit_repo.get_by_id_for_update(invoice_id)
    elif provider_invoice_id is not None:
        invoice = await deposit_repo.get_by_provider_invoice_id_for_update(
            provider_invoice_id
        )
    else:
        raise ConfirmDepositError("Provide invoice_id or provider_invoice_id")

    if invoice is None:
        raise ConfirmDepositError("Invoice not found")
    if not allow_admin_override and invoice.user_tg_id != actor_user_tg_id:
        raise ConfirmDepositError("You cannot confirm another user's invoice")
    if invoice.status == DepositInvoiceStatusEnum.PAID:
        return False

    invoice.status = DepositInvoiceStatusEnum.PAID
    await deposit_repo.save(invoice)

    balance = await balance_repo.get_or_create(invoice.user_tg_id)
    balance.amount = balance.amount + invoice.amount
    await balance_repo.save(balance)
    await transaction_repo.create(
        user_tg_id=invoice.user_tg_id,
        amount=invoice.amount,
        type_=TransactionTypeEnum.CREDIT,
        reason=TransactionReasonEnum.DEPOSIT,
        external_id=invoice.provider_invoice_id or f"deposit:{invoice.id}",
    )
    logger.info(
        "confirm_deposit: invoice_id=%s actor_user_tg_id=%s credited_user_tg_id=%s",
        invoice.id,
        actor_user_tg_id,
        invoice.user_tg_id,
    )
    return True
