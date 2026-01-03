
from __future__ import annotations

from app.common.database.objects import DBMatchEvent
from app.common.constants import EventType
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    match_id: int,
    type: EventType,
    data: dict = {},
    session: Session = ...
) -> DBMatchEvent:
    session.add(
        m := DBMatchEvent(
            match_id=match_id,
            type=type.value,
            data=data
        )
    )
    session.flush()
    session.refresh(m)
    return m

@session_wrapper
def fetch_last(match_id: int, session: Session = ...) -> DBMatchEvent | None:
    return session.query(DBMatchEvent) \
        .filter(DBMatchEvent.match_id == match_id) \
        .order_by(DBMatchEvent.time.desc()) \
        .first()

@session_wrapper
def fetch_last_by_type(match_id: int, type: int, session: Session = ...) -> DBMatchEvent | None:
    return session.query(DBMatchEvent) \
        .filter(DBMatchEvent.match_id == match_id) \
        .filter(DBMatchEvent.type == type) \
        .order_by(DBMatchEvent.time.desc()) \
        .first()

@session_wrapper
def fetch_all(match_id: int, session: Session = ...) -> List[DBMatchEvent]:
    return session.query(DBMatchEvent) \
        .filter(DBMatchEvent.match_id == match_id) \
        .all()

@session_wrapper
def fetch_all_after_time(
    match_id: int,
    after: datetime,
    session: Session = ...
) -> List[DBMatchEvent]:
    return session.query(DBMatchEvent) \
        .filter(DBMatchEvent.match_id == match_id) \
        .filter(DBMatchEvent.time > after) \
        .order_by(DBMatchEvent.time.asc()) \
        .all()

@session_wrapper
def delete_all(match_id: int, session: Session = ...) -> None:
    session.query(DBMatchEvent) \
        .filter(DBMatchEvent.match_id == match_id) \
        .delete()
    session.flush()
