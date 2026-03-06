# Demo Platform

Демо-версия Telegram-бота игровой платформы с упрощённой бизнес-логикой и фокусом на архитектуру, качество кода и эксплуатационные практики.

В репозитории реализованы модульная структура, ручной DI, typed use case'ы, контроль конкурентного доступа, файловое логирование, graceful shutdown и базовый startup recovery.

## Что здесь демонстрируется

- **Прагматичная луковичная архитектура с DDD-подходом.** Модули разделены по bounded context'ам, но без искусственного усложнения и лишних абстракций.
- **Manual DI и composition root.** Зависимости собираются в `app/main.py`, а use case'ы получают репозитории и провайдеры явно.
- **Runtime-механизмы.** Есть throttling, per-user lock, draining during shutdown, файловые логи и контролируемое завершение приложения.
- **Typed Python backend.** Проект покрыт `mypy`, `pytest`, использует `pydantic-settings`, SQLAlchemy 2 async и value objects.
- **Вертикальные сценарии.** В демо оставлены восемь ключевых сценариев, оформленных как отдельные use case'ы.

## Архитектурные принципы

- **Луковичная архитектура с TDD и DDD подходами.** Бизнес-операции выделены в use case'ы, а инфраструктура остаётся на внешних границах приложения.
- **Минимум слоёв.** Нет дублирования `domain`/`persistence` моделей ради теоретической чистоты.
- **Интерфейсы не создаются заранее.** Абстракции вводятся только там, где они реально дают ценность.
- **Use case важнее framework glue.** Aiogram и SQLAlchemy остаются на границах, бизнес-операции выделены явно.
- **Инфраструктурные механизмы включены в код.** В проекте реализованы throttling, user lock, error handling, graceful shutdown и startup recovery.

## Структура проекта

```text
app/
├── core/                     # Общая инфраструктура и bootstrap-логика
│   ├── config.py             # Настройки из .env через pydantic-settings
│   ├── database/             # Engine, sessionmaker, Base, create_database, close_engine
│   ├── logging/              # Пакет логирования: setup, factory, handlers
│   ├── recovery.py           # Оркестрация startup recovery
│   ├── recovery_helpers.py   # SQL helper-функции recovery
│   └── value_objects/        # Money
│
├── modules/                  # Бизнес-модули
│   ├── identity/             # Пользователь и синхронизация профиля
│   ├── game/                 # Игровые сессии и ставки
│   └── wallet/               # Баланс, транзакции, депозиты и вывод
│
├── presentation/             # Telegram delivery layer
│   ├── bot.py                # Run / shutdown orchestration
│   ├── bot_helpers.py        # Сборка Bot/Dispatcher и lifecycle helpers
│   ├── handlers/             # Команды бота
│   └── middlewares/          # DB session, throttling, lock, draining, error handling
│
└── main.py                   # Composition root приложения
```

## Реализованные сценарии

| # | Сценарий | Use case |
|---|----------|----------|
| 1 | Синхронизация пользователя | `sync_user_info` |
| 2 | Старт новой игры | `start_game` |
| 3 | Ставка в активной игре | `place_bet` |
| 4 | Завершение игры | `finish_game` |
| 5 | Просмотр кошелька и статистики | `get_wallet_and_stats_overview` |
| 6 | Запрос инвойса на депозит | `request_deposit_invoice` |
| 7 | Подтверждение депозита | `confirm_deposit` |
| 8 | Вывод средств | `withdraw_funds` |

## Reliability Features

- **Throttle middleware.** Ограничивает частоту запросов на пользователя в заданном временном окне.
- **User lock middleware.** Сериализует критичные действия и снижает риск гонок при повторных апдейтах.
- **Error handling middleware.** Централизованно логирует неожиданные ошибки и отдаёт единый fallback-ответ.
- **Draining during shutdown.** Во время остановки новые апдейты не принимаются в работу.
- **Graceful shutdown.** Бот и БД закрываются контролируемо, с таймаутами и логированием.
- **Startup recovery.** При старте логируются pending депозиты и незавершённые игровые сессии.

## Технологии

- Python 3.11+
- aiogram 3
- SQLAlchemy 2 async
- asyncpg
- pydantic-settings
- pytest
- mypy
- Poetry

## Быстрый старт

### Требования

- Python 3.11+
- PostgreSQL
- [Poetry](https://python-poetry.org/)

### Установка

```bash
poetry install --with test
```

Создайте локальный `.env` на основе шаблона:

```bash
cp .env.example .env
```

Для Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Минимально нужно заполнить:

- `BOT_TOKEN`
- `DATABASE_URL`

Опционально можно настроить:

- `ADMIN_USER_IDS`
- `LOG_LEVEL`, `LOG_DIR`
- `DEFAULT_BALANCE`, `DEFAULT_BET_AMOUNT`
- `SHUTDOWN_TIMEOUT_SECONDS`
- `THROTTLE_WINDOW_SECONDS`, `THROTTLE_LIMIT_PER_USER`
- `USER_ACTION_LOCK_TTL_SECONDS`

### Запуск

Перед первым запуском нужно применить миграции Alembic:

```bash
poetry run alembic upgrade head
```

После этого приложение можно запускать обычной командой:

```bash
poetry run python -m app.main
```

Логи пишутся в консоль и в `logs/app.log` с ротацией по размеру.

## Проверка качества

```bash
poetry run pytest
poetry run mypy app
```

В проекте есть:

- smoke-тест на импорт приложения
- unit-тесты `Money`
- тесты на ключевые use case'ы кошелька и игры

## CI/CD

Для проекта добавлен workflow `GitHub Actions` в `.github/workflows/demo-ci-cd.yml`.

- На `pull request` и `push` в `main` / `develop` запускаются `pytest` и `mypy`.
- На `push` и `workflow_dispatch` после успешных проверок собираются `wheel` и `sdist`.
- По тегу вида `demo-v*` workflow публикует GitHub Release с артефактами сборки.

Workflow проверяет код, собирает артефакты и публикует релизные сборки по тегам `demo-v*`.

## Ограничения demo-версии

- Платёжный провайдер заменён на `DemoPaymentProvider`.
- Сценарии упрощены и не претендуют на полноту production-логики.
- Нет FSM и сложного UX-слоя, команды текстовые и намеренно простые.
- Recovery на старте только диагностический: он логирует проблемные состояния, но не чинит их автоматически.
- Полноценный production deployment pipeline и внешние интеграции в проект не включены.

## Особенности demo-формата

- Бизнес-логика упрощена до восьми основных сценариев.
- Платёжная интеграция заменена на демонстрационный провайдер `DemoPaymentProvider`.
- Инфраструктурные части проекта оставлены в рабочем виде: тесты, типизация, сборка пакета и GitHub Actions workflow.

## Лицензия

MIT
