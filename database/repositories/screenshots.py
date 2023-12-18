
from __future__ import annotations

from app.common.database.objects import DBScreenshot
from sqlalchemy.orm import Session

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    hidden: bool,
    session: Session | None = None
) -> DBScreenshot:
    session.add(
        ss := DBScreenshot(
            user_id,
            hidden
        )
    )
    session.commit()
    session.refresh(ss)
    return ss

@session_wrapper
def fetch_by_id(
    id: int,
    session: Session | None = None
) -> DBScreenshot | None:
    return session.query(DBScreenshot) \
            .filter(DBScreenshot.id == id) \
            .first()
