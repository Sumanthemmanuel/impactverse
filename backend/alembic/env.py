import asyncio
from logging.config import fileConfig
from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Import settings and models
from app.config import settings
from app.models import Base  # This imports all models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = str(settings.DATABASE_URL)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        # Enable extensions
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS "postgis"'))
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS "vector"'))
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS "pg_trgm"'))
        context.run_migrations()

async def run_async_migrations() -> None:
    connectable = create_async_engine(
        str(settings.DATABASE_URL),
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
