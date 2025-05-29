
from __future__ import annotations

from app.common.database.repositories import events
from app.common.database.objects import DBMatch

from sqlalchemy.orm import Session

from .wrapper import session_wrapper

@session_wrapper
def create(
    name: str,
    bancho_id: int,
    creator_id: int,
    session: Session = ...
) -> DBMatch:
    session.add(
        m := DBMatch(
            name,
            creator_id,
            bancho_id
        )
    )
    session.commit()
    session.refresh(m)
    return m

@session_wrapper
def fetch_by_id(id: int, session: Session = ...) -> DBMatch | None:
    return session.query(DBMatch) \
        .filter(DBMatch.id == id) \
        .first()

@session_wrapper
def fetch_by_bancho_id(id: int, session: Session = ...) -> DBMatch | None:
    return session.query(DBMatch) \
        .filter(DBMatch.bancho_id == id) \
        .first()
        
@session_wrapper
def exists(id: int, session: Session = ...) -> bool:
    return session.query(DBMatch) \
        .filter(DBMatch.id == id) \
        .count() > 0

@session_wrapper
def update(id: int, updates: dict, session: Session = ...) -> None:
    session.query(DBMatch) \
        .filter(DBMatch.id == id) \
        .update(updates)
    session.commit()

@session_wrapper
def delete(id: int, session: Session = ...) -> None:
    # Delete events first
    events.delete_all(id)

    session.query(DBMatch) \
        .filter(DBMatch.id == id) \
        .delete()
    session.commit()
