import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ---------------------------------------------------------------------------
# Ensure the service root and any sibling libs are importable
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Optionally add a shared /libs directory if it exists beside the service root
LIBS_DIR = os.path.join(os.path.dirname(BASE_DIR), "libs")
if os.path.isdir(LIBS_DIR):
    sys.path.insert(0, LIBS_DIR)

# ---------------------------------------------------------------------------
# Import settings and all models so Alembic can detect schema changes
# ---------------------------------------------------------------------------
from app.core.config import settings  # noqa: E402
from app.infrastructure.database.base import Base  # noqa: E402

# Register all ORM models with Base.metadata
import app.subscription_plans.models.subscription_plan  # noqa: F401, E402
import app.tenant_subscriptions.models.tenant_subscription  # noqa: F401, E402
import app.usage_records.models.usage_record  # noqa: F401, E402
import app.invoices.models.invoice  # noqa: F401, E402

# ---------------------------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------------------------
config = context.config

# Inject DATABASE_URL from settings so alembic.ini's %(DATABASE_URL)s resolves
config.set_main_option("DATABASE_URL", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
