"""Ограничение частоты запросов по пользователю."""

from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from app.core.config import get_settings
from app.core.logging import get_logger
from app.presentation.middlewares.utils import (
    answer_event,
    cast_event_to_update,
    extract_user_id,
)

logger = get_logger(__name__)
_THROTTLE_REJECT_TEXT = "Слишком много запросов. Подождите немного."


class ThrottleMiddleware(BaseMiddleware):
    """Ограничивает число запросов от одного пользователя в единицу времени."""

    def __init__(self) -> None:
        super().__init__()
        self._user_timestamps: dict[int, deque[float]] = {}
        self._lock = asyncio.Lock()
        self._last_seen: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        settings = get_settings()
        window = settings.throttle_window_seconds
        limit = settings.throttle_limit_per_user

        user_id = extract_user_id(event)
        if user_id is None:
            return await handler(cast_event_to_update(event), data)

        now = time.monotonic()
        should_reject = False
        async with self._lock:
            if user_id not in self._user_timestamps:
                self._user_timestamps[user_id] = deque(maxlen=limit * 2)
            q = self._user_timestamps[user_id]
            while q and now - q[0] > window:
                q.popleft()
            self._last_seen[user_id] = now
            if len(q) >= limit:
                logger.warning("Throttle: user_id=%s limit=%s", user_id, limit)
                should_reject = True
            else:
                q.append(now)

            stale_before = now - max(window * 2, 60.0)
            stale_users = [
                stale_user_id
                for stale_user_id, last_seen in self._last_seen.items()
                if last_seen < stale_before
            ]
            for stale_user_id in stale_users:
                self._user_timestamps.pop(stale_user_id, None)
                self._last_seen.pop(stale_user_id, None)

        if should_reject:
            await answer_event(event, _THROTTLE_REJECT_TEXT)
            return None

        return await handler(cast_event_to_update(event), data)
