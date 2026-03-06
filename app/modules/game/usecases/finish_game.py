"""Завершение игры и фиксация результата в кошельке."""

from app.core.value_objects.money import Money
from app.modules.game.repositories import GameSessionRepository
from app.modules.wallet.enums import TransactionReasonEnum, TransactionTypeEnum
from app.modules.wallet.repositories import BalanceRepository, TransactionRepository


class FinishGameError(Exception):
    """Ошибка завершения игры, если сценарий не может быть выполнен."""

    pass


async def finish_game(
    game_session_repo: GameSessionRepository,
    balance_repo: BalanceRepository,
    transaction_repo: TransactionRepository,
    user_tg_id: int,
    won: bool,
    win_amount: Money,
) -> None:
    """Фиксирует результат активной игровой сессии и обновляет кошелёк.

    При победе начисляет `win_amount`, при поражении не меняет баланс
    дополнительно. Вызывает `FinishGameError`, если активная сессия не найдена.
    """
    game_session = await game_session_repo.get_active_by_user_tg_id(user_tg_id)
    if game_session is None:
        raise FinishGameError("No active game session")

    game_session.set_result(won=won, win_amount=win_amount)
    await game_session_repo.save(game_session)

    if won and win_amount.is_positive():
        balance = await balance_repo.get_by_user_tg_id(user_tg_id)
        if balance is not None:
            balance.amount = balance.amount + win_amount
            await balance_repo.save(balance)
        await transaction_repo.create(
            user_tg_id=user_tg_id,
            amount=win_amount,
            type_=TransactionTypeEnum.CREDIT,
            reason=TransactionReasonEnum.GAME_WIN,
        )
