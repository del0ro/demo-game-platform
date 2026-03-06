"""Сценарии использования модуля wallet."""

from app.modules.wallet.usecases.confirm_deposit import confirm_deposit
from app.modules.wallet.usecases.get_wallet_and_stats_overview import (
    get_wallet_and_stats_overview,
)
from app.modules.wallet.usecases.request_deposit_invoice import request_deposit_invoice
from app.modules.wallet.usecases.withdraw_funds import withdraw_funds

__all__ = [
    "get_wallet_and_stats_overview",
    "request_deposit_invoice",
    "confirm_deposit",
    "withdraw_funds",
]

