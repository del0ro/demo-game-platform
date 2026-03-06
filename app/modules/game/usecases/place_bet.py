"""Размещение ставки: списание средств и обновление игровой сессии."""

import logging

from app.core.value_objects.money import Money
from app.modules.game.enums import GameSessionStatus
from app.modules.game.repositories import GameSessionRepository
from app.modules.wallet.enums import TransactionReasonEnum, TransactionTypeEnum
from app.modules.wallet.repositories import BalanceRepository, TransactionRepository


class PlaceBetError(Exception):
    """Ошибка размещения ставки."""

    pass


logger = logging.getLogger(__name__)


async def place_bet(
    game_session_repo: GameSessionRepository,
    balance_repo: BalanceRepository,
    transaction_repo: TransactionRepository,
    user_tg_id: int,
    bet_amount: Money,
) -> None:
    """Списывает ставку, активирует игру при необходимости и обновляет сессию.

    Состояние сессии меняется только после проверки баланса, чтобы при ошибке
    нехватки средств игра не переходила в `ACTIVE`.
    """
    game_session = await game_session_repo.get_pending_or_active_one_by_user_tg_id(user_tg_id)
    if game_session is None:
        raise PlaceBetError("No active or pending game session")

    balance = await balance_repo.get_by_user_tg_id(user_tg_id)
    if balance is None or balance.amount < bet_amount:
        raise PlaceBetError("Insufficient balance")

    if game_session.status == GameSessionStatus.PENDING_START:
        game_session.activate()

    balance.amount = balance.amount - bet_amount
    await transaction_repo.create(
        user_tg_id=user_tg_id,
        amount=bet_amount,
        type_=TransactionTypeEnum.DEBIT,
        reason=TransactionReasonEnum.BET,
    )
    game_session.update_bet_amount(bet_amount)

    await balance_repo.save(balance)
    await game_session_repo.save(game_session)
    logger.info("place_bet: user_tg_id=%s amount=%s", user_tg_id, bet_amount)
