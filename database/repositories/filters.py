
from __future__ import annotations

from app.common.database.objects import DBChatFilter
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    name: str,
    pattern: str,
    replacement: str | None = None,
    block: bool = False,
    block_timeout_duration: int | None = None,
    session: Session = ...
) -> DBChatFilter:
    session.add(
        f := DBChatFilter(
            name=name,
            pattern=pattern,
            replacement=replacement,
            block=block,
            block_timeout_duration=block_timeout_duration
        )
    )
    session.flush()
    session.refresh(f)
    return f

@session_wrapper
def fetch_by_name(name: str, session: Session = ...) -> DBChatFilter | None:
    return session.query(DBChatFilter) \
        .filter(DBChatFilter.name == name) \
        .first()
        
@session_wrapper
def fetch_all(session: Session = ...) -> List[DBChatFilter]:
    return session.query(DBChatFilter) \
        .order_by(DBChatFilter.created_at.asc()) \
        .all()

@session_wrapper
def fetch_all_blocked(session: Session = ...) -> List[DBChatFilter]:
    return session.query(DBChatFilter) \
        .filter(DBChatFilter.block == True) \
        .all()
