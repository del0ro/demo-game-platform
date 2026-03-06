"""Тесты ключевых сценариев использования demo-проекта."""

from __future__ import annotations

import asyncio
from typing import cast

import pytest

from app.core.value_objects.money import Money
from app.modules.game.enums import GameSessionStatus, GameType
from app.modules.game.models import GameSessionModel
from app.modules.game.repositories import GameSessionRepository
from app.modules.game.usecases.place_bet import PlaceBetError, place_bet
from app.modules.wallet.enums import DepositInvoiceStatusEnum
from app.modules.wallet.models import BalanceModel, DepositInvoiceModel
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
from app.modules.wallet.usecases.request_deposit_invoice import (
    RequestedDepositInvoice,
    request_deposit_invoice,
)


class FakeGameSessionRepository:
    def __init__(self, game_session: GameSessionModel | None) -> None:
        self.game_session = game_session
        self.saved: list[GameSessionModel] = []

    async def get_pending_or_active_one_by_user_tg_id(
        self, user_tg_id: int
    ) -> GameSessionModel | None:
        if self.game_session and self.game_session.user_tg_id == user_tg_id:
            return self.game_session
        return None

    async def save(self, game_session: GameSessionModel) -> None:
        self.saved.append(game_session)


class FakeBalanceRepository:
    def __init__(self, balance: BalanceModel | None) -> None:
        self.balance = balance
        self.saved: list[BalanceModel] = []

    async def get_by_user_tg_id(self, user_tg_id: int) -> BalanceModel | None:
        if self.balance and self.balance.user_tg_id == user_tg_id:
            return self.balance
        return None

    async def get_or_create(self, user_tg_id: int) -> BalanceModel:
        if self.balance is None:
            self.balance = BalanceModel(user_tg_id=user_tg_id, amount=Money("0"))
        return self.balance

    async def save(self, balance: BalanceModel) -> None:
        self.saved.append(balance)


class FakeTransactionRepository:
    def __init__(self) -> None:
        self.created: list[dict[str, object]] = []

    async def create(self, **kwargs: object) -> None:
        self.created.append(kwargs)


class FakeDepositInvoiceRepository:
    def __init__(self, invoice: DepositInvoiceModel | None) -> None:
        self.invoice = invoice
        self.saved: list[DepositInvoiceModel] = []

    async def create(self, invoice: DepositInvoiceModel) -> DepositInvoiceModel:
        invoice.id = 123
        self.invoice = invoice
        return invoice

    async def get_by_id_for_update(
        self, invoice_id: int
    ) -> DepositInvoiceModel | None:
        if self.invoice and self.invoice.id == invoice_id:
            return self.invoice
        return None

    async def get_by_provider_invoice_id_for_update(
        self, provider_invoice_id: str
    ) -> DepositInvoiceModel | None:
        if (
            self.invoice
            and self.invoice.provider_invoice_id == provider_invoice_id
        ):
            return self.invoice
        return None

    async def save(self, invoice: DepositInvoiceModel) -> None:
        self.saved.append(invoice)


class FakePaymentProvider:
    def create_invoice(self, amount: Money, user_id: int) -> tuple[str, str]:
        return (f"https://demo.test/pay/{user_id}", f"provider-{user_id}-{amount}")


def test_place_bet_does_not_activate_session_without_balance() -> None:
    game_session = GameSessionModel(
        user_tg_id=100,
        game_type=GameType.HILO,
        bet_amount=Money("1"),
        status=GameSessionStatus.PENDING_START,
    )
    balance = BalanceModel(user_tg_id=100, amount=Money("0.50"))

    with pytest.raises(PlaceBetError, match="Insufficient balance"):
        asyncio.run(
            place_bet(
                game_session_repo=cast(
                    GameSessionRepository, FakeGameSessionRepository(game_session)
                ),
                balance_repo=cast(BalanceRepository, FakeBalanceRepository(balance)),
                transaction_repo=cast(TransactionRepository, FakeTransactionRepository()),
                user_tg_id=100,
                bet_amount=Money("1"),
            )
        )

    assert game_session.status == GameSessionStatus.PENDING_START


def test_request_deposit_invoice_returns_invoice_metadata() -> None:
    result = asyncio.run(
        request_deposit_invoice(
            deposit_invoice_repo=cast(
                DepositInvoiceRepository, FakeDepositInvoiceRepository(None)
            ),
            user_tg_id=100,
            amount=Money("10"),
            provider=cast(DemoPaymentProvider, FakePaymentProvider()),
        )
    )

    assert isinstance(result, RequestedDepositInvoice)
    assert result.invoice_id == 123
    assert result.payment_url == "https://demo.test/pay/100"
    assert result.provider_invoice_id.startswith("provider-100-")


def test_confirm_deposit_rejects_other_user() -> None:
    invoice = DepositInvoiceModel(
        user_tg_id=42,
        amount=Money("10"),
        provider_invoice_id="provider-42-10",
        status=DepositInvoiceStatusEnum.PENDING,
    )
    invoice.id = 7

    with pytest.raises(
        ConfirmDepositError, match="You cannot confirm another user's invoice"
    ):
        asyncio.run(
            confirm_deposit(
                deposit_repo=cast(
                    DepositInvoiceRepository, FakeDepositInvoiceRepository(invoice)
                ),
                balance_repo=cast(BalanceRepository, FakeBalanceRepository(None)),
                transaction_repo=cast(
                    TransactionRepository, FakeTransactionRepository()
                ),
                actor_user_tg_id=100,
                invoice_id=7,
            )
        )


def test_confirm_deposit_is_idempotent_for_paid_invoice() -> None:
    invoice = DepositInvoiceModel(
        user_tg_id=42,
        amount=Money("10"),
        provider_invoice_id="provider-42-10",
        status=DepositInvoiceStatusEnum.PAID,
    )
    invoice.id = 9
    transaction_repo = FakeTransactionRepository()

    result = asyncio.run(
        confirm_deposit(
                deposit_repo=cast(
                    DepositInvoiceRepository, FakeDepositInvoiceRepository(invoice)
                ),
                balance_repo=cast(BalanceRepository, FakeBalanceRepository(None)),
                transaction_repo=cast(TransactionRepository, transaction_repo),
            actor_user_tg_id=42,
            invoice_id=9,
        )
    )

    assert result is False
    assert transaction_repo.created == []


def test_confirm_deposit_credits_balance_once() -> None:
    invoice = DepositInvoiceModel(
        user_tg_id=42,
        amount=Money("10"),
        provider_invoice_id="provider-42-10",
        status=DepositInvoiceStatusEnum.PENDING,
    )
    invoice.id = 10
    balance = BalanceModel(user_tg_id=42, amount=Money("5"))
    transaction_repo = FakeTransactionRepository()

    result = asyncio.run(
        confirm_deposit(
                deposit_repo=cast(
                    DepositInvoiceRepository, FakeDepositInvoiceRepository(invoice)
                ),
                balance_repo=cast(BalanceRepository, FakeBalanceRepository(balance)),
                transaction_repo=cast(TransactionRepository, transaction_repo),
            actor_user_tg_id=42,
            invoice_id=10,
        )
    )

    assert result is True
    assert balance.amount == Money("15")
    assert len(transaction_repo.created) == 1
    assert transaction_repo.created[0]["external_id"] == "provider-42-10"
