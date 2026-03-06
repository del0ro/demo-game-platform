"""Репозиторий деталей HiLo по игровой сессии."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.game.models.game_hilo_details import GameHiloDetailsModel


class GameHiloDetailsRepository:
    """Создаёт и читает шаги HiLo, связанные с игровой сессией."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, detail: GameHiloDetailsModel) -> GameHiloDetailsModel:
        self._session.add(detail)
        await self._session.flush()
        await self._session.refresh(detail)
        return detail

    async def get_by_game_session_id(
        self, game_session_id: int
    ) -> tuple[GameHiloDetailsModel, ...]:
        stmt = (
            select(GameHiloDetailsModel)
            .where(GameHiloDetailsModel.game_session_id == game_session_id)
            .order_by(GameHiloDetailsModel.roll_number.asc())
        )
        result = await self._session.execute(stmt)
        return tuple(result.scalars().all())
