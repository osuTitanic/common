
from app.common.database.objects import DBStamp
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper, SessionProvider

@session_wrapper
def create(
    user_id: int,
    description: str,
    icon_url: str,
    stamp_url: str | None = None,
    session: Session = SessionProvider
) -> DBStamp:
    session.add(
        badge := DBStamp(
            user_id=user_id,
            created=datetime.now(),
            icon=icon_url,
            url=stamp_url,
            description=description
        )
    )
    session.flush()
    session.refresh(badge)
    return badge

@session_wrapper
def fetch_one(
    id: int,
    session: Session = SessionProvider
) -> DBStamp | None:
    return session.query(DBStamp) \
        .filter(DBStamp.id == id) \
        .first()

@session_wrapper
def fetch_all(
    user_id: int,
    session: Session = SessionProvider
) -> List[DBStamp]:
    return session.query(DBStamp) \
        .filter(DBStamp.user_id == user_id) \
        .order_by(DBStamp.created.desc()) \
        .all()

@session_wrapper
def update(
    id: int,
    updates: dict,
    session: Session = SessionProvider
) -> int:
    rows = session.query(DBStamp) \
        .filter(DBStamp.id == id) \
        .update(updates)
    session.flush()
    return rows

@session_wrapper
def delete(
    id: int,
    session: Session = SessionProvider
) -> int:
    rows = session.query(DBStamp) \
        .filter(DBStamp.id == id) \
        .delete()
    session.flush()
    return rows
