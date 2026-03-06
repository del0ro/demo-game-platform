"""Репозиторий игровых сессий пользователя."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.game.enums import GameSessionStatus
from app.modules.game.models.game_session import GameSessionModel


class GameSessionRepository:
    """Работает с игровыми сессиями по пользователю и статусу."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, game_session_id: int) -> GameSessionModel | None:
        return await self._session.get(GameSessionModel, game_session_id)

    async def create(self, game_session: GameSessionModel) -> GameSessionModel:
        self._session.add(game_session)
        await self._session.flush()
        await self._session.refresh(game_session)
        return game_session

    async def save(self, game_session: GameSessionModel) -> None:
        await self._session.flush()

    async def get_active_by_user_tg_id(
        self, user_tg_id: int
    ) -> GameSessionModel | None:
        stmt = (
            select(GameSessionModel)
            .where(
                GameSessionModel.user_tg_id == user_tg_id,
                GameSessionModel.status == GameSessionStatus.ACTIVE,
            )
            .order_by(GameSessionModel.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_or_active_one_by_user_tg_id(
        self, user_tg_id: int
    ) -> GameSessionModel | None:
        """Возвращает последнюю сессию пользователя в статусе `PENDING_START` или `ACTIVE`."""
        stmt = (
            select(GameSessionModel)
            .where(
                GameSessionModel.user_tg_id == user_tg_id,
                GameSessionModel.status.in_([
                    GameSessionStatus.PENDING_START,
                    GameSessionStatus.ACTIVE,
                ]),
            )
            .order_by(GameSessionModel.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_or_active_by_user_tg_id(
        self, user_tg_id: int
    ) -> tuple[GameSessionModel, ...]:
        stmt = (
            select(GameSessionModel)
            .where(
                GameSessionModel.user_tg_id == user_tg_id,
                GameSessionModel.status.in_([
                    GameSessionStatus.PENDING_START,
                    GameSessionStatus.ACTIVE,
                ]),
            )
            .order_by(GameSessionModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return tuple(result.scalars().all())
