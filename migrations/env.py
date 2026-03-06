import asyncio
import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.core.database.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


def _load_env_from_dotenv() -> None:
    """Пытается загрузить `.env` для Alembic без дополнительных зависимостей."""
    # demo/ is the project root; env.py lives in demo/migrations/
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_from_dotenv()


def _import_demo_models() -> None:
    """Импортирует все ORM-модели demo-приложения для заполнения metadata."""
    from app.modules.game.models import (  # noqa: F401
        GameHiloDetailsModel,
        GameSessionModel,
        GameSettingsModel,
    )
    from app.modules.identity.models import UserModel  # noqa: F401
    from app.modules.wallet.models import (  # noqa: F401
        BalanceModel,
        DepositInvoiceModel,
        TransactionModel,
    )

db_url = os.getenv("DATABASE_URL")
if db_url:
    # override sqlalchemy.url from alembic.ini using DATABASE_URL from .env
    config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

_import_demo_models()
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Запускает миграции в офлайн-режиме.

    В этом режиме для конфигурации контекста используется только URL
    подключения без создания `Engine`. Вызовы `context.execute()` пишут
    SQL-скрипт в выходной поток Alembic.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Создаёт `Engine` и связывает соединение с контекстом миграций."""

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запускает миграции в онлайн-режиме."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
