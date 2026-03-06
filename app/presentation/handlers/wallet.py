"""Обработчики кошелька и платёжных операций demo-проекта."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.modules.wallet.providers import DemoPaymentProvider
from app.modules.wallet.repositories import (
    BalanceRepository,
    DepositInvoiceRepository,
    TransactionRepository,
)
from app.modules.wallet.usecases.confirm_deposit import (
    ConfirmDepositError,
    confirm_deposit,
)
from app.modules.wallet.usecases.get_wallet_and_stats_overview import (
    get_wallet_and_stats_overview,
)
from app.modules.wallet.usecases.request_deposit_invoice import (
    RequestDepositInvoiceError,
    request_deposit_invoice,
)
from app.modules.wallet.usecases.withdraw_funds import (
    WithdrawFundsError,
    withdraw_funds,
)
from app.presentation.handlers.wallet_helpers import (
    format_deposit_invoice_text,
    format_wallet_text,
    log_wallet_action,
    parse_invoice_id_argument,
    parse_money_argument,
)

logger = get_logger(__name__)
wallet_router = Router(name="wallet_router")


@wallet_router.message(Command("wallet"))
async def wallet_handler(message: Message, session: AsyncSession) -> None:
    """Показывает баланс и последние транзакции пользователя."""
    if message.from_user is None:
        return

    log_wallet_action(message, "Wallet")

    balance_repo = BalanceRepository(session)
    transaction_repo = TransactionRepository(session)

    overview = await get_wallet_and_stats_overview(
        balance_repo=balance_repo,
        transaction_repo=transaction_repo,
        user_tg_id=message.from_user.id,
        transactions_limit=10,
    )

    await message.answer(
        format_wallet_text(
            balance=overview["balance"],
            recent_transactions=list(overview["recent_transactions"]),
        )
    )


@wallet_router.message(Command("deposit"), F.text)
async def deposit_handler(message: Message, session: AsyncSession) -> None:
    """Создаёт счёт на депозит."""
    if message.from_user is None:
        return

    log_wallet_action(message, "Deposit")

    amount = parse_money_argument(message)
    if amount is None:
        await message.answer("Использование: /deposit <сумма>")
        return

    deposit_repo = DepositInvoiceRepository(session)
    provider = DemoPaymentProvider()

    try:
        async with session.begin():
            invoice = await request_deposit_invoice(
                deposit_invoice_repo=deposit_repo,
                user_tg_id=message.from_user.id,
                amount=amount,
                provider=provider,
            )
    except RequestDepositInvoiceError as e:
        await message.answer(str(e))
        return

    await message.answer(format_deposit_invoice_text(amount, invoice))


@wallet_router.message(Command("withdraw"), F.text)
async def withdraw_handler(message: Message, session: AsyncSession) -> None:
    """Выводит средства со счёта пользователя."""
    if message.from_user is None:
        return

    log_wallet_action(message, "Withdraw")

    amount = parse_money_argument(message)
    if amount is None:
        await message.answer("Использование: /withdraw <сумма>")
        return

    balance_repo = BalanceRepository(session)
    transaction_repo = TransactionRepository(session)

    try:
        async with session.begin():
            await withdraw_funds(
                balance_repo=balance_repo,
                transaction_repo=transaction_repo,
                user_tg_id=message.from_user.id,
                amount=amount,
            )
    except WithdrawFundsError as e:
        await message.answer(str(e))
        return

    await message.answer(f"✅ Вывод на сумму ${amount} выполнен.")


@wallet_router.message(Command("confirm_deposit"), F.text)
async def confirm_deposit_handler(message: Message, session: AsyncSession) -> None:
    """Подтверждает депозит по `invoice_id`."""
    if message.from_user is None:
        return

    log_wallet_action(message, "Confirm deposit")

    invoice_id = parse_invoice_id_argument(message)
    if invoice_id is None:
        await message.answer("Использование: /confirm_deposit <invoice_id>")
        return

    settings = get_settings()
    deposit_repo = DepositInvoiceRepository(session)
    balance_repo = BalanceRepository(session)
    transaction_repo = TransactionRepository(session)

    try:
        async with session.begin():
            was_processed = await confirm_deposit(
                deposit_repo=deposit_repo,
                balance_repo=balance_repo,
                transaction_repo=transaction_repo,
                actor_user_tg_id=message.from_user.id,
                allow_admin_override=message.from_user.id in settings.admin_user_ids,
                invoice_id=invoice_id,
            )
    except ConfirmDepositError as e:
        await message.answer(str(e))
        return

    if was_processed:
        await message.answer("✅ Депозит подтверждён, средства зачислены.")
    else:
        await message.answer("ℹ️ Этот депозит уже был подтверждён ранее.")
