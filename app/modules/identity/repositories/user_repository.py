"""Репозиторий пользователей по `tg_id`."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.models.user import UserModel


class UserRepository:
    """Работает с `UserModel`, от которого напрямую зависят use case'ы."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_tg_id(self, tg_id: int) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.tg_id == tg_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: UserModel) -> UserModel:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def save(self, user: UserModel) -> None:
        await self._session.flush()
