"""Блокировка по пользователю: одна критичная операция за раз на пользователя."""

from __future__ import annotations

import asyncio
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
_USER_LOCK_REJECT_TEXT = "Операция занята. Попробуйте через несколько секунд."


class UserLockMiddleware(BaseMiddleware):
    """Сериализует обработку апдейтов по user_id: один апдейт за раз на пользователя."""

    def __init__(self) -> None:
        super().__init__()
        self._user_locks: dict[int, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        self._last_used: dict[int, float] = {}

    def _get_user_lock(self, user_id: int) -> asyncio.Lock:
        if user_id not in self._user_locks:
            self._user_locks[user_id] = asyncio.Lock()
        return self._user_locks[user_id]

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = extract_user_id(event)
        if user_id is None:
            return await handler(cast_event_to_update(event), data)

        async with self._global_lock:
            user_lock = self._get_user_lock(user_id)
            self._last_used[user_id] = asyncio.get_running_loop().time()

        timeout = get_settings().user_action_lock_ttl_seconds
        try:
            await asyncio.wait_for(user_lock.acquire(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("UserLock timeout user_id=%s", user_id)
            await answer_event(event, _USER_LOCK_REJECT_TEXT)
            return None

        try:
            return await handler(cast_event_to_update(event), data)
        finally:
            user_lock.release()
            async with self._global_lock:
                now = asyncio.get_running_loop().time()
                self._last_used[user_id] = now
                stale_before = now - max(get_settings().user_action_lock_ttl_seconds * 2, 60.0)
                stale_users = [
                    stale_user_id
                    for stale_user_id, last_used in self._last_used.items()
                    if last_used < stale_before
                    and stale_user_id in self._user_locks
                    and not self._user_locks[stale_user_id].locked()
                ]
                for stale_user_id in stale_users:
                    self._user_locks.pop(stale_user_id, None)
                    self._last_used.pop(stale_user_id, None)
