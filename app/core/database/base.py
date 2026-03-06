"""Базовый декларативный класс SQLAlchemy для demo-приложения."""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """База для всех ORM-моделей demo-приложения."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
