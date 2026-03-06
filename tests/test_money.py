"""Unit-тесты для объекта-значения `Money`."""

from typing import Any, cast

import pytest
from decimal import Decimal

from app.core.value_objects.money import Money


def test_money_from_str() -> None:
    m = Money("10.50")
    assert m.amount == Decimal("10.50")


def test_money_from_int() -> None:
    m = Money(10)
    assert m.amount == Decimal("10")


def test_money_from_float() -> None:
    m = Money(10.5)
    assert m.amount == Decimal("10.5")


def test_money_add() -> None:
    a = Money("1.5")
    b = Money("2.5")
    c = a + b
    assert c.amount == Decimal("4")


def test_money_sub() -> None:
    a = Money("5")
    b = Money("2")
    c = a - b
    assert c.amount == Decimal("3")


def test_money_mul() -> None:
    a = Money("10")
    b = a * 2
    assert b.amount == Decimal("20")


def test_money_compare() -> None:
    a = Money("5")
    b = Money("10")
    assert a < b
    assert a <= b
    assert b > a
    assert b >= a
    assert a != b
    assert a == Money("5")


def test_money_invalid_raises() -> None:
    with pytest.raises(ValueError):
        Money("")
    with pytest.raises(ValueError):
        Money("abc")
    with pytest.raises(TypeError):
        Money("1") + cast(Any, 1)


def test_money_is_zero() -> None:
    assert Money("0").is_zero is True
    assert Money("0.01").is_zero is False


def test_money_is_positive() -> None:
    assert Money("0.01").is_positive() is True
    assert Money("0").is_positive() is False
