
from __future__ import annotations

from app.common.database.objects import DBLog
from sqlalchemy.orm import Session
from datetime import datetime

from .wrapper import session_wrapper

@session_wrapper
def create(
    message: str,
    level: str,
    type: str,
    session: Session = ...
) -> DBLog:
    session.add(
        log := DBLog(
            message=message,
            level=level,
            type=type,
            time=datetime.now()
        )
    )
    session.flush()
    return log

# TODO: Create fetch queries
