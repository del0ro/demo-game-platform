"""Списание средств и создание транзакции на вывод."""

import logging

from app.core.value_objects.money import Money
from app.modules.wallet.enums import TransactionReasonEnum, TransactionTypeEnum
from app.modules.wallet.repositories import BalanceRepository, TransactionRepository


class WithdrawFundsError(Exception):
    """Ошибка вывода средств, если сценарий не может быть выполнен."""

    pass


logger = logging.getLogger(__name__)


async def withdraw_funds(
    balance_repo: BalanceRepository,
    transaction_repo: TransactionRepository,
    user_tg_id: int,
    amount: Money,
    details: str = "",
) -> None:
    """Списывает деньги с баланса и создаёт транзакцию вывода.

    В demo-версии вывод применяется сразу, без отдельного статуса ожидания.
    Вызывает `WithdrawFundsError`, если средств недостаточно или сумма
    меньше либо равна нулю.
    """
    if amount.amount <= 0:
        raise WithdrawFundsError("Amount must be positive")

    balance = await balance_repo.get_by_user_tg_id(user_tg_id)
    if balance is None or balance.amount < amount:
        raise WithdrawFundsError("Insufficient balance")

    balance.amount = balance.amount - amount
    await balance_repo.save(balance)
    await transaction_repo.create(
        user_tg_id=user_tg_id,
        amount=amount,
        type_=TransactionTypeEnum.DEBIT,
        reason=TransactionReasonEnum.WITHDRAW_TRANSFER,
    )
    logger.info("withdraw_funds: user_tg_id=%s amount=%s", user_tg_id, amount)
