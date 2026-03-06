"""Тип SQLAlchemy для `Money`, сохраняемого как `Numeric` в БД."""

from decimal import Decimal
from typing import Any

from sqlalchemy import Numeric
from sqlalchemy.types import TypeDecorator

from app.core.value_objects.money import Money


class MoneyType(TypeDecorator):
    """Тип колонки: `Numeric` в БД и `Money` в Python-коде."""

    impl = Numeric
    cache_ok = True

    def __init__(self, precision: int = 12, scale: int = 4, **kwargs: Any) -> None:
        self._precision = precision
        self._scale = scale
        super().__init__(**kwargs)

    def load_dialect_impl(self, dialect: Any) -> Any:
        return dialect.type_descriptor(Numeric(self._precision, self._scale))

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, Money):
            return value.amount
        if isinstance(value, (Decimal, int, float, str)):
            return Decimal(value) if not isinstance(value, Decimal) else value
        raise TypeError(f"Expected Money or number, got {type(value)}")

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        return Money(value)
