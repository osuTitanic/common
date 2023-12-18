
from __future__ import annotations

from app.common.database.objects import DBLog
from sqlalchemy.orm import Session

from .wrapper import session_wrapper

@session_wrapper
def create(
    message: str,
    level: str,
    type: str,
    session: Session | None = None
) -> DBLog:
    session.add(
        log := DBLog(
            message,
            level,
            type
        )
    )
    session.commit()
    return log

# TODO: Create fetch queries
