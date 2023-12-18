
from __future__ import annotations

from app.common.database.objects import DBMatchEvent
from app.common.constants import EventType
from sqlalchemy.orm import Session
from typing import List, Optional

from .wrapper import session_wrapper

@session_wrapper
def create(
    match_id: int,
    type: EventType,
    data: dict = {},
    session: Session | None = None
) -> DBMatchEvent:
    session.add(
        m := DBMatchEvent(
            match_id,
            type.value,
            data
        )
    )
    session.commit()
    session.refresh(m)
    return m

@session_wrapper
def fetch_last(match_id: int, session: Session | None = None) -> Optional[DBMatchEvent]:
    return session.query(DBMatchEvent) \
        .filter(DBMatchEvent.match_id == match_id) \
        .order_by(DBMatchEvent.time.desc()) \
        .first()

@session_wrapper
def fetch_last_by_type(match_id: int, type: int, session: Session | None = None) -> Optional[DBMatchEvent]:
    return session.query(DBMatchEvent) \
        .filter(DBMatchEvent.match_id == match_id) \
        .filter(DBMatchEvent.type == type) \
        .order_by(DBMatchEvent.time.desc()) \
        .first()

@session_wrapper
def fetch_all(match_id: int, session: Session | None = None) -> List[DBMatchEvent]:
    return session.query(DBMatchEvent) \
        .filter(DBMatchEvent.match_id == match_id) \
        .all()

@session_wrapper
def delete_all(match_id: int, session: Session | None = None) -> None:
    session.query(DBMatchEvent) \
        .filter(DBMatchEvent.match_id == match_id) \
        .delete()
    session.commit()
