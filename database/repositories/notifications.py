
from __future__ import annotations

from ..objects import DBNotification
from .wrapper import session_wrapper

from sqlalchemy.orm import Session
from sqlalchemy import func

@session_wrapper
def create(
    user_id: int,
    type: int,
    header: str,
    content: str,
    read: bool = False,
    link: str | None = None,
    session: Session | None = None
) -> DBNotification:
    session.add(
        n := DBNotification(
            user_id,
            type,
            header,
            content,
            link,
            read
        )
    )
    session.commit()
    session.refresh(n)
    return n

@session_wrapper
def fetch_one(id: int, session: Session | None = None) -> int:
    return session.query(DBNotification) \
        .filter(DBNotification.id == id) \
        .first()

@session_wrapper
def fetch_count(
    user_id: int,
    read: bool | None = False,
    session: Session | None = None
) -> int:
    if read is None:
        return session.query(func.count(DBNotification)) \
            .filter(DBNotification.user_id == user_id) \
            .scalar()

    return session.query(func.count(DBNotification)) \
        .filter(DBNotification.user_id == user_id) \
        .filter(DBNotification.read == read) \
        .scalar()

@session_wrapper
def fetch_all(
    user_id: int,
    read: bool | None = False,
    session: Session | None = None
) -> int:
    if read is None:
        return session.query(DBNotification) \
            .filter(DBNotification.user_id == user_id) \
            .all()

    return session.query(DBNotification) \
        .filter(DBNotification.user_id == user_id) \
        .filter(DBNotification.read == read) \
        .all()

@session_wrapper
def update(
    id: int,
    updates: dict,
    session: Session | None = None
) -> int:
    rows = session.query(DBNotification) \
        .filter(DBNotification.id == id) \
        .update(updates)
    session.commit()
    return rows
