"""Глобальный слой обработки ошибок для presentation."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from app.core.logging import get_logger
from app.presentation.middlewares.utils import answer_event, cast_event_to_update

logger = get_logger(__name__)

_GENERIC_ERROR_TEXT = "❌ Произошла внутренняя ошибка. Попробуйте позже."


class ErrorHandlingMiddleware(BaseMiddleware):
    """Логирует неожиданные ошибки и отправляет пользователю единый ответ."""

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(cast_event_to_update(event), data)
        except Exception:
            logger.exception("Unhandled presentation error")
            await answer_event(event, _GENERIC_ERROR_TEXT)
            return None
