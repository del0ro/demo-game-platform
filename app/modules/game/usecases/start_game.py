"""Запуск новой игровой сессии для пользователя."""

from app.core.value_objects.money import Money
from app.modules.game.enums import GameSessionStatus, GameType
from app.modules.game.models import GameSessionModel
from app.modules.game.repositories import (
    GameSessionRepository,
    GameSettingsRepository,
)
from app.modules.wallet.repositories import BalanceRepository


class StartGameError(Exception):
    """Ошибка запуска игры, если сценарий не может быть выполнен."""

    pass


async def start_game(
    game_session_repo: GameSessionRepository,
    game_settings_repo: GameSettingsRepository,
    balance_repo: BalanceRepository,
    user_tg_id: int,
    bet_amount: Money | None = None,
    default_bet_amount: Money | None = None,
    check_balance: bool = True,
) -> GameSessionModel:
    """Создаёт новую игровую сессию со статусом `PENDING_START`.

    Если `bet_amount` не передан, используется значение из пользовательских
    настроек игры или `default_bet_amount`. Вызывает `StartGameError`, если у
    пользователя уже есть активная или ожидающая сессия либо недостаточно
    средств.
    """
    existing = await game_session_repo.get_pending_or_active_by_user_tg_id(user_tg_id)
    if existing:
        raise StartGameError("User already has an active or pending game session")

    settings = await game_settings_repo.get_or_create(
        user_tg_id, default_bet_amount=default_bet_amount or Money("0.1")
    )
    amount = bet_amount if bet_amount is not None else settings.bet_amount

    if check_balance:
        balance = await balance_repo.get_or_create(user_tg_id)
        if balance.amount < amount:
            raise StartGameError("Insufficient balance")

    game_session = GameSessionModel(
        user_tg_id=user_tg_id,
        game_type=GameType.HILO,
        bet_amount=amount,
        status=GameSessionStatus.PENDING_START,
    )
    return await game_session_repo.create(game_session)
