"""Синхронизация пользователя из данных Telegram: создание или обновление и создание баланса при необходимости."""

import logging

from app.core.value_objects.money import Money
from app.modules.identity.models import UserModel
from app.modules.identity.repositories import UserRepository
from app.modules.wallet.repositories import BalanceRepository

logger = logging.getLogger(__name__)


async def sync_user_info(
    user_repo: UserRepository,
    balance_repo: BalanceRepository,
    tg_id: int,
    username: str | None = None,
    name: str | None = None,
    default_balance: Money | None = None,
) -> UserModel:
    """Убеждается, что пользователь существует и профиль актуален; для новых создаёт баланс.

    Возвращает пользователя (созданного или обновлённого). Выполняется в транзакции вызывающего.
    """
    user = await user_repo.get_by_tg_id(tg_id)

    if user is None:
        user = UserModel(
            tg_id=tg_id,
            username=username,
            name=name,
        )
        await user_repo.create(user)
        await balance_repo.get_or_create(
            user_tg_id=tg_id,
            default_amount=default_balance if default_balance is not None else Money("0"),
        )
        logger.info("sync_user_info: создан пользователь tg_id=%s", tg_id)
        return user

    if user.username != username or user.name != name:
        user.update_from_telegram(name=name, username=username)
        await user_repo.save(user)

    return user
