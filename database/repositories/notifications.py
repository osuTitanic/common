
from __future__ import annotations

from ..objects import DBNotification
from .wrapper import session_wrapper

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

@session_wrapper
def create(
    user_id: int,
    type: int,
    header: str,
    content: str,
    read: bool = False,
    link: str | None = None,
    session: Session = ...
) -> DBNotification:
    session.add(
        n := DBNotification(
            user_id=user_id,
            type=type,
            header=header,
            content=content,
            link=link,
            read=read,
            time=datetime.now()
        )
    )
    session.flush()
    session.refresh(n)
    return n

@session_wrapper
def fetch_one(id: int, session: Session = ...) -> int:
    return session.query(DBNotification) \
        .filter(DBNotification.id == id) \
        .first()

@session_wrapper
def fetch_count(
    user_id: int,
    read: bool | None = False,
    session: Session = ...
) -> int:
    if read is None:
        count = session.query(func.count(DBNotification.id)) \
            .filter(DBNotification.user_id == user_id) \
            .scalar()

    else:
        count = session.query(func.count(DBNotification.id)) \
            .filter(DBNotification.user_id == user_id) \
            .filter(DBNotification.read == read) \
            .scalar()

    return count or 0

@session_wrapper
def fetch_all(
    user_id: int,
    read: bool | None = False,
    until: datetime | None = None,
    session: Session = ...
) -> List[DBNotification]:
    query = session.query(DBNotification) \
        .filter(DBNotification.user_id == user_id)

    if read is not None:
        query = query.filter(DBNotification.read == read)

    if until is not None:
        query = query.filter(DBNotification.time > until)

    return query.all()

@session_wrapper
def update(
    id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBNotification) \
        .filter(DBNotification.id == id) \
        .update(updates)
    session.flush()
    return rows

@session_wrapper
def update_by_user_id(
    user_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBNotification) \
        .filter(DBNotification.user_id == user_id) \
        .update(updates)
    session.flush()
    return rows

@session_wrapper
def delete(
    id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBNotification) \
        .filter(DBNotification.id == id) \
        .delete()
    session.flush()
    return rows

@session_wrapper
def delete_by_type(
    user_id: int,
    type: int,
    session: Session = ...
) -> int:
    rows = session.query(DBNotification) \
        .filter(DBNotification.user_id == user_id) \
        .filter(DBNotification.type == type) \
        .filter(DBNotification.read == False) \
        .delete()
    session.flush()
    return rows
