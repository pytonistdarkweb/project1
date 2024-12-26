from logging.config import fileConfig
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import pool
from alembic import context


from app.Infrastructure.database import Base
from app.domain.models import User
from app.domain.models import Task
from app.domain.models import TaskTranslation


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/postgres"


if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)


target_metadata = Base.metadata

def run_migrations_offline():
    """Запуск миграций в оффлайн-режиме."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """Настройка контекста для онлайн-миграций."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Запуск миграций в онлайн-режиме с асинхронным движком."""
    connectable: AsyncEngine = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
