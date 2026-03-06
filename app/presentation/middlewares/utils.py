"""Общие вспомогательные функции для presentation middleware."""

from __future__ import annotations

from typing import cast

from aiogram.types import CallbackQuery, Message, TelegramObject, Update


def cast_event_to_update(event: TelegramObject) -> Update:
    """Приводит event к типу `Update` для сигнатуры aiogram middleware."""
    return cast(Update, event)


def extract_user_id(event: TelegramObject) -> int | None:
    """Извлекает user_id из message/update-события, если он доступен."""
    if isinstance(event, Update):
        if event.message and event.message.from_user:
            return event.message.from_user.id
        if event.callback_query and event.callback_query.from_user:
            return event.callback_query.from_user.id
        return None

    if isinstance(event, Message) and event.from_user:
        return event.from_user.id

    if isinstance(event, CallbackQuery) and event.from_user:
        return event.from_user.id

    return None


async def answer_event(event: TelegramObject, text: str) -> None:
    """Отправляет текстовый ответ для поддерживаемых Telegram-событий."""
    if isinstance(event, Message):
        await event.answer(text)
        return

    if isinstance(event, CallbackQuery):
        await event.answer()
        if isinstance(event.message, Message):
            await event.message.answer(text)
        return

    if isinstance(event, Update):
        if event.message is not None:
            await event.message.answer(text)
            return
        if event.callback_query is not None:
            await event.callback_query.answer()
            if isinstance(event.callback_query.message, Message):
                await event.callback_query.message.answer(text)
