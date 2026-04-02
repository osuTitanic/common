
from app.common.database.objects import DBBadge
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper, SessionProvider

@session_wrapper
def create(
    user_id: int,
    description: str,
    icon_url: str,
    badge_url: str | None = None,
    session: Session = SessionProvider
) -> DBBadge:
    session.add(
        badge := DBBadge(
            user_id=user_id,
            created=datetime.now(),
            badge_icon=icon_url,
            badge_url=badge_url,
            badge_description=description
        )
    )
    session.flush()
    session.refresh(badge)
    return badge

@session_wrapper
def fetch_one(
    id: int,
    session: Session = SessionProvider
) -> DBBadge | None:
    return session.query(DBBadge) \
        .filter(DBBadge.id == id) \
        .first()

@session_wrapper
def fetch_all(
    user_id: int,
    session: Session = SessionProvider
) -> List[DBBadge]:
    return session.query(DBBadge) \
        .filter(DBBadge.user_id == user_id) \
        .order_by(DBBadge.created.desc()) \
        .all()

@session_wrapper
def update(
    id: int,
    updates: dict,
    session: Session = SessionProvider
) -> int:
    rows = session.query(DBBadge) \
        .filter(DBBadge.id == id) \
        .update(updates)
    session.flush()
    return rows

@session_wrapper
def delete(
    id: int,
    session: Session = SessionProvider
) -> int:
    rows = session.query(DBBadge) \
        .filter(DBBadge.id == id) \
        .delete()
    session.flush()
    return rows
