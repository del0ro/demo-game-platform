"""Фабрика логгеров для demo-приложения."""

from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    """Возвращает логгер с указанным именем."""
    return logging.getLogger(name)


logger = get_logger("app")
