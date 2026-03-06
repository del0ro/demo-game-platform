"""Middleware, который создаёт сессию БД на каждый апдейт.

Добавляет в `data["session"]` сессию SQLAlchemy.
Транзакциями управляют сами обработчики, чтобы commit завершался до Telegram I/O.
"""

from typing import TYPE_CHECKING, Any, Awaitable, Callable, cast

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import async_sessionmaker as AsyncSessionMaker


class DatabaseMiddleware(BaseMiddleware):
    """Создаёт сессию БД для каждого апдейта и передаёт её в `data["session"]`."""

    def __init__(self, sessionmaker: "AsyncSessionMaker[AsyncSession]") -> None:
        super().__init__()
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self.sessionmaker() as session:
            data["session"] = session
            return await handler(cast(Update, event), data)
