from typing import Generator

from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_db as _get_db
from app.core.security import get_current_user  # noqa: F401 — re-export for routes


def get_db() -> Generator[Session, None, None]:
    """Database session dependency. Re-exports from session module."""
    yield from _get_db()
