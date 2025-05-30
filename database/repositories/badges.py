
from __future__ import annotations

from app.common.database.objects import DBBadge
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    description: str,
    icon_url: str,
    badge_url: str | None = None,
    session: Session = ...
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
    session.commit()
    session.refresh(badge)
    return badge

@session_wrapper
def fetch_one(
    id: int,
    session: Session = ...
) -> DBBadge | None:
    return session.query(DBBadge) \
        .filter(DBBadge.id == id) \
        .first()

@session_wrapper
def fetch_all(
    user_id: int,
    session: Session = ...
) -> List[DBBadge]:
    return session.query(DBBadge) \
        .filter(DBBadge.user_id == user_id) \
        .order_by(DBBadge.created.desc()) \
        .all()

@session_wrapper
def update(
    id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBBadge) \
        .filter(DBBadge.id == id) \
        .update(updates)
    session.commit()
    return rows

@session_wrapper
def delete(
    id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBBadge) \
        .filter(DBBadge.id == id) \
        .delete()
    session.commit()
    return rows
