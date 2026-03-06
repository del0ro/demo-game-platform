"""Публичный API пакета логирования demo-приложения."""

from app.core.logging.factory import get_logger, logger
from app.core.logging.setup import setup_logging

__all__ = ["get_logger", "logger", "setup_logging"]
