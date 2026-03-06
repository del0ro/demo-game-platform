"""Общие обработчики для demo-бота."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.value_objects.money import Money
from app.modules.identity.repositories import UserRepository
from app.modules.identity.usecases.sync_user_info import sync_user_info
from app.modules.wallet.repositories import BalanceRepository

logger = get_logger(__name__)
common_router = Router(name="common_router")


def _build_welcome_text() -> str:
    """Форматирует приветственное сообщение."""
    return (
        "<b>Добро пожаловать в demo-платформу.</b>"
    )


@common_router.message(Command("start"))
async def start_handler(message: Message, session: AsyncSession) -> None:
    """Регистрирует пользователя, синхронизирует профиль и отправляет приветствие."""
    if message.from_user is None:
        return

    tg_id = message.from_user.id
    settings = get_settings()
    default_balance = (
        Money(settings.default_balance) if settings.default_balance else Money("0")
    )

    logger.info(
        "Start | %s (%s)",
        message.from_user.full_name,
        tg_id,
    )

    user_repo = UserRepository(session)
    balance_repo = BalanceRepository(session)

    async with session.begin():
        await sync_user_info(
            user_repo=user_repo,
            balance_repo=balance_repo,
            tg_id=tg_id,
            username=message.from_user.username,
            name=message.from_user.full_name,
            default_balance=default_balance,
        )

    await message.answer(_build_welcome_text())
