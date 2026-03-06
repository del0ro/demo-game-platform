"""Вспомогательные настройки и фабрики для конфигурации логирования."""

from __future__ import annotations

import logging
import sys
from logging import Handler
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import get_settings

DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def resolve_logging_settings(
    level: str | None,
    log_dir: str | None,
) -> tuple[str, str | None]:
    """Подмешивает значения из `Settings`, если они не переданы явно."""
    if level is None or log_dir is None:
        settings = get_settings()
        if level is None:
            level = settings.log_level
        if log_dir is None:
            log_dir = settings.log_dir
    return level, log_dir


def create_stream_handler(
    log_level: int,
    formatter: logging.Formatter,
) -> Handler:
    """Создаёт консольный обработчик логов."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    return handler


def create_rotating_file_handler(
    log_dir: str,
    log_level: int,
    formatter: logging.Formatter,
    max_bytes: int,
    backup_count: int,
) -> Handler:
    """Создаёт файловый обработчик логов с ротацией."""
    dir_path = Path(log_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        dir_path / "app.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    return handler
