"""Репозиторий пользовательских игровых настроек."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.value_objects.money import Money
from app.modules.game.models.game_settings import GameSettingsModel


class GameSettingsRepository:
    """Работает с пользовательскими настройками игры, например ставкой по умолчанию."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_tg_id(
        self, user_tg_id: int
    ) -> GameSettingsModel | None:
        stmt = select(GameSettingsModel).where(
            GameSettingsModel.user_tg_id == user_tg_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        user_tg_id: int,
        default_bet_amount: Money | None = None,
    ) -> GameSettingsModel:
        existing = await self.get_by_user_tg_id(user_tg_id)
        if existing is not None:
            return existing
        settings = GameSettingsModel(
            user_tg_id=user_tg_id,
            bet_amount=default_bet_amount if default_bet_amount is not None else Money("0.1"),
        )
        self._session.add(settings)
        await self._session.flush()
        await self._session.refresh(settings)
        return settings

    async def save(self, game_settings: GameSettingsModel) -> None:
        await self._session.flush()
