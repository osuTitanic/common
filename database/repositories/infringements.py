
from __future__ import annotations

from app.common.database.objects import DBInfringement
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    action: int,
    length: datetime,
    description: str | None = None,
    is_permanent: bool = False,
    session: Session = ...
) -> DBInfringement:
    session.add(
        i := DBInfringement(
            user_id,
            action,
            length,
            description,
            is_permanent
        )
    )
    session.commit()
    session.refresh(i)
    return i

@session_wrapper
def fetch_recent(user_id: int, session: Session = ...) -> DBInfringement | None:
    return session.query(DBInfringement) \
        .filter(DBInfringement.user_id == user_id) \
        .order_by(DBInfringement.id.desc()) \
        .first()

@session_wrapper
def fetch_recent_by_action(user_id: int, action: int, session: Session = ...) -> DBInfringement | None:
    return session.query(DBInfringement) \
        .filter(DBInfringement.user_id == user_id) \
        .filter(DBInfringement.action == action) \
        .order_by(DBInfringement.id.desc()) \
        .first()

@session_wrapper
def fetch_recent_until(
    user_id: int,
    until: timedelta = timedelta(days=30),
    session: Session = ...
) -> List[DBInfringement]:
    return session.query(DBInfringement) \
        .filter(DBInfringement.user_id == user_id) \
        .filter(DBInfringement.time > (datetime.now() - until)) \
        .order_by(DBInfringement.id.desc()) \
        .all()

@session_wrapper
def fetch_all(user_id: int, session: Session = ...) -> List[DBInfringement]:
    return session.query(DBInfringement) \
        .filter(DBInfringement.user_id == user_id) \
        .order_by(DBInfringement.id.desc()) \
        .all()

@session_wrapper
def fetch_all_by_action(user_id: int, action: int, session: Session = ...) -> List[DBInfringement]:
    return session.query(DBInfringement) \
        .filter(DBInfringement.user_id == user_id) \
        .filter(DBInfringement.action == action) \
        .order_by(DBInfringement.time.desc()) \
        .all()

@session_wrapper
def delete_by_id(id: int, session: Session = ...) -> None:
    session.query(DBInfringement) \
        .filter(DBInfringement.id == id) \
        .delete()

@session_wrapper
def delete_old(
    user_id: int,
    delete_after=timedelta(weeks=5),
    remove_permanent=False,
    session: Session = ...
) -> int:
    if not remove_permanent:
        return session.query(DBInfringement) \
                .filter(DBInfringement.user_id == user_id) \
                .filter(DBInfringement.time < datetime.now() - delete_after) \
                .filter(DBInfringement.is_permanent == False) \
                .delete()

    return session.query(DBInfringement) \
                .filter(DBInfringement.user_id == user_id) \
                .filter(DBInfringement.time < datetime.now() - delete_after) \
                .delete()
