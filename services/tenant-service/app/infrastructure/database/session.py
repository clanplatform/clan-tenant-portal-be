from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.infrastructure.database.base import Base
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables() -> None:
    from sqlalchemy.exc import IntegrityError

    # Import all models so Base.metadata is populated
    from app.tenants.models.tenant import Tenant  # noqa: F401
    from app.tenant_settings.models.tenant_setting import TenantSetting  # noqa: F401
    from app.tenant_domains.models.tenant_domain import TenantDomain  # noqa: F401
    from app.feature_flags.models.feature_flag import TenantFeatureFlag  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except IntegrityError:
        pass


def check_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
