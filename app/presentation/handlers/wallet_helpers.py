"""Вспомогательные функции для обработчиков кошелька."""

from __future__ import annotations

from typing import TypedDict

from aiogram.types import Message

from app.core.logging import get_logger
from app.core.value_objects.money import Money
from app.modules.wallet.usecases.request_deposit_invoice import RequestedDepositInvoice

logger = get_logger(__name__)


class WalletTransactionSummary(TypedDict):
    """Структура одной транзакции в сообщении кошелька."""

    amount: Money
    type: str
    reason: str
    created_at: str


def parse_money_argument(message: Message) -> Money | None:
    """Парсит сумму из команды `/command <amount>`."""
    if message.text is None:
        return None
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    try:
        return Money(parts[1].strip())
    except ValueError:
        return None


def parse_invoice_id_argument(message: Message) -> int | None:
    """Парсит `invoice_id` из команды `/confirm_deposit <invoice_id>`."""
    if message.text is None:
        return None
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    try:
        return int(parts[1].strip())
    except ValueError:
        return None


def format_wallet_text(
    balance: Money,
    recent_transactions: list[WalletTransactionSummary],
) -> str:
    """Форматирует сообщение кошелька."""
    lines = [
        "💎 <b>Кошелёк</b>",
        "",
        f"<blockquote>💰 Баланс: ${balance}</blockquote>",
    ]
    if recent_transactions:
        lines.append("")
        lines.append("<b>Последние операции:</b>")
        for tx in recent_transactions[:5]:
            lines.append(
                f"• {tx['type']} {tx['reason']}: ${tx['amount']} — {str(tx['created_at'])[:19]}"
            )
    return "\n".join(lines)


def format_deposit_invoice_text(
    amount: Money, invoice: RequestedDepositInvoice
) -> str:
    """Форматирует сообщение со счётом на депозит."""
    return (
        "💳 <b>Счёт создан.</b>\n\n"
        f"<blockquote>ID счёта: {invoice.invoice_id}</blockquote>\n"
        f"<blockquote>Сумма: ${amount}</blockquote>\n"
        f"Ссылка на оплату (demo): {invoice.payment_url}\n\n"
        f"Для подтверждения отправьте: <code>/confirm_deposit {invoice.invoice_id}</code>"
    )


def log_wallet_action(message: Message, action: str) -> None:
    """Логирует действие пользователя в модуле кошелька."""
    if message.from_user is None:
        return
    logger.info(
        "%s | %s (%s)",
        action,
        message.from_user.full_name,
        message.from_user.id,
    )
