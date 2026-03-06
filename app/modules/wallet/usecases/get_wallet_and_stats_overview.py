"""Получение баланса кошелька и краткой истории транзакций."""

from typing import TypedDict

from app.core.value_objects.money import Money
from app.modules.wallet.repositories import BalanceRepository, TransactionRepository


class TransactionSummary(TypedDict):
    """Сводка по одной транзакции для отображения в обзоре."""

    amount: Money
    type: str
    reason: str
    created_at: str


class WalletOverview(TypedDict):
    """Сводные данные по кошельку пользователя."""

    balance: Money
    recent_transactions: list[TransactionSummary]


async def get_wallet_and_stats_overview(
    balance_repo: BalanceRepository,
    transaction_repo: TransactionRepository,
    user_tg_id: int,
    transactions_limit: int = 20,
) -> WalletOverview:
    """Возвращает текущий баланс и последние транзакции пользователя."""
    balance = await balance_repo.get_or_create(user_tg_id)
    txs = await transaction_repo.list_recent_by_user(
        user_tg_id, limit=transactions_limit
    )

    return WalletOverview(
        balance=balance.amount,
        recent_transactions=[
            TransactionSummary(
                amount=tx.amount,
                type=tx.type.value,
                reason=tx.reason.value,
                created_at=tx.created_at.isoformat() if tx.created_at else "",
            )
            for tx in txs
        ],
    )
