"""Объект-значение `Money` для demo-приложения."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation


class Money:
    """Объект-значение для денежных сумм.

    Валидируется при создании и может принимать отрицательные значения, если
    это требуется для расчётов финансового результата.
    """

    def __init__(self, amount: Decimal | float | int | str | Money) -> None:
        try:
            if isinstance(amount, str):
                amount = Decimal(amount.replace(",", ".").strip())
            elif isinstance(amount, (int, float)):
                amount = Decimal(str(amount))
            elif isinstance(amount, Money):
                amount = amount.amount
            elif not isinstance(amount, Decimal):
                raise TypeError(f"Unsupported type: {type(amount)}")
        except (ValueError, InvalidOperation):
            raise ValueError("Invalid amount")
        if not amount.is_finite():
            raise ValueError("Invalid amount")
        self._amount = amount

    @property
    def amount(self) -> Decimal:
        return self._amount

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        return Money(self._amount + other._amount)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        return Money(self._amount - other._amount)

    def __mul__(self, other: Decimal | float | int) -> "Money":
        if isinstance(other, (int, float)):
            other = Decimal(str(other))
        if not isinstance(other, Decimal):
            raise TypeError("Can only multiply by Decimal, float or int")
        return Money(self._amount * other)

    def __rmul__(self, other: Decimal | float | int) -> "Money":
        return self.__mul__(other)

    def __truediv__(self, other: Decimal | float | int) -> "Money":
        if isinstance(other, (int, float)):
            other = Decimal(str(other))
        if not isinstance(other, Decimal):
            raise TypeError("Can only divide by Decimal, float or int")
        if other == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self._amount / other)

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        return self._amount < other._amount

    def __le__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        return self._amount <= other._amount

    def __gt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        return self._amount > other._amount

    def __ge__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        return self._amount >= other._amount

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self._amount == other._amount

    def __hash__(self) -> int:
        return hash(self._amount)

    def __str__(self) -> str:
        return f"{float(self._amount.quantize(Decimal('0.01'))):.2f}"

    def __repr__(self) -> str:
        return f"Money({self._amount})"

    @property
    def is_zero(self) -> bool:
        return self._amount == 0

    def is_positive(self) -> bool:
        return self._amount > 0
