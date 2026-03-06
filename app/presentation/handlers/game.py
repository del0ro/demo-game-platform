"""Обработчики игровых сценариев demo-проекта."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.value_objects.money import Money
from app.modules.game.usecases.finish_game import FinishGameError, finish_game
from app.modules.game.usecases.place_bet import PlaceBetError, place_bet
from app.modules.game.usecases.start_game import StartGameError, start_game
from app.presentation.handlers.game_helpers import (
    build_finish_game_text,
    build_start_game_text,
    get_game_repositories,
    log_game_action,
    parse_money_argument,
)

logger = get_logger(__name__)
game_router = Router(name="game_router")


@game_router.message(Command("game"))
async def start_game_handler(message: Message, session: AsyncSession) -> None:
    """Создаёт новую игровую сессию."""
    if message.from_user is None:
        return

    log_game_action(message, "Start game")

    settings = get_settings()
    default_bet = (
        Money(settings.default_bet_amount)
        if settings.default_bet_amount
        else Money("0.1")
    )
    repos = get_game_repositories(session)

    try:
        async with session.begin():
            game_session = await start_game(
                game_session_repo=repos["game_session_repo"],
                game_settings_repo=repos["game_settings_repo"],
                balance_repo=repos["balance_repo"],
                user_tg_id=message.from_user.id,
                default_bet_amount=default_bet,
                check_balance=True,
            )
    except StartGameError as e:
        await message.answer(str(e))
        return

    await message.answer(build_start_game_text(game_session.bet_amount))


@game_router.message(Command("bet"), F.text)
async def place_bet_handler(message: Message, session: AsyncSession) -> None:
    """Списывает ставку и активирует игру."""
    if message.from_user is None:
        return

    log_game_action(message, "Place bet")

    amount = parse_money_argument(message)
    if amount is None:
        await message.answer("Использование: /bet <сумма>")
        return

    repos = get_game_repositories(session)
    try:
        async with session.begin():
            await place_bet(
                game_session_repo=repos["game_session_repo"],
                balance_repo=repos["balance_repo"],
                transaction_repo=repos["transaction_repo"],
                user_tg_id=message.from_user.id,
                bet_amount=amount,
            )
    except PlaceBetError as e:
        await message.answer(str(e))
        return

    await message.answer(f"✅ Ставка ${amount} принята.")


@game_router.message(Command("finish_win"))
async def finish_game_win_handler(message: Message, session: AsyncSession) -> None:
    """Завершает игру выигрышем."""
    if message.from_user is None:
        return

    log_game_action(message, "Finish game win")

    win_amount = parse_money_argument(message) or Money("0")
    repos = get_game_repositories(session)

    try:
        async with session.begin():
            await finish_game(
                game_session_repo=repos["game_session_repo"],
                balance_repo=repos["balance_repo"],
                transaction_repo=repos["transaction_repo"],
                user_tg_id=message.from_user.id,
                won=True,
                win_amount=win_amount,
            )
    except FinishGameError as e:
        await message.answer(str(e))
        return

    await message.answer(build_finish_game_text(won=True, win_amount=win_amount))


@game_router.message(Command("finish_lose"))
async def finish_game_lose_handler(message: Message, session: AsyncSession) -> None:
    """Завершает игру проигрышем."""
    if message.from_user is None:
        return

    log_game_action(message, "Finish game lose")

    repos = get_game_repositories(session)
    try:
        async with session.begin():
            await finish_game(
                game_session_repo=repos["game_session_repo"],
                balance_repo=repos["balance_repo"],
                transaction_repo=repos["transaction_repo"],
                user_tg_id=message.from_user.id,
                won=False,
                win_amount=Money("0"),
            )
    except FinishGameError as e:
        await message.answer(str(e))
        return

    await message.answer(build_finish_game_text(won=False, win_amount=Money("0")))
