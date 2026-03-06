"""Роутеры команд и колбэков."""

from app.presentation.handlers.common import common_router
from app.presentation.handlers.game import game_router
from app.presentation.handlers.wallet import wallet_router

__all__ = ["common_router", "game_router", "wallet_router"]
