"""Публичная функция настройки логирования."""

from __future__ import annotations

import logging

from app.core.logging.settings import (
    DEFAULT_FORMAT,
    create_rotating_file_handler,
    create_stream_handler,
    resolve_logging_settings,
)

_configured = False


def setup_logging(
    level: str | None = None,
    format_string: str = DEFAULT_FORMAT,
    stream: bool = True,
    log_dir: str | None = None,
    log_file_max_bytes: int = 2 * 1024 * 1024,
    log_file_backup_count: int = 3,
) -> None:
    """Настраивает корневой логгер demo-приложения.

    Конфигурация вызывается из composition root до инициализации остальной
    инфраструктуры. Повторный вызов безопасен и не приводит к накоплению
    дублирующихся handlers.
    """
    global _configured
    if _configured:
        return

    level, log_dir = resolve_logging_settings(level=level, log_dir=log_dir)

    log_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()

    for handler in root.handlers[:]:
        root.removeHandler(handler)

    formatter = logging.Formatter(format_string)

    if stream:
        root.addHandler(create_stream_handler(log_level=log_level, formatter=formatter))

    if log_dir:
        root.addHandler(
            create_rotating_file_handler(
                log_dir=log_dir,
                log_level=log_level,
                formatter=formatter,
                max_bytes=log_file_max_bytes,
                backup_count=log_file_backup_count,
            )
        )

    root.setLevel(log_level)
    _configured = True
