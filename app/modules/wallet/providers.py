"""Заглушка платёжного провайдера для demo-приложения."""

from app.core.value_objects.money import Money


class DemoPaymentProvider:
    """Демо-реализация провайдера, которая возвращает фиктивный платёжный URL."""

    def create_invoice(self, amount: Money, user_id: int) -> tuple[str, str]:
        """Создаёт фиктивный инвойс и возвращает URL оплаты и ID провайдера."""
        fake_id = f"demo_inv_{user_id}_{amount.amount}"
        return f"https://demo.example.com/pay/{fake_id}", fake_id

    def check_invoice_status(self, provider_invoice_id: str) -> str:
        """Возвращает статус инвойса.

        В demo-версии всегда возвращает `pending`, если статус не изменён
        вручную во внешнем коде.
        """
        return "pending"
