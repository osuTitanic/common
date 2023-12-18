
from __future__ import annotations

from app.common.database.objects import DBMessage
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    sender: str,
    target: str,
    message: str,
    session: Session | None = None
) -> DBMessage:
    session.add(
        msg := DBMessage(
            sender,
            target,
            message
        )
    )
    session.commit()
    session.refresh(msg)
    return msg

@session_wrapper
def fetch_recent(
    target: str = '#osu',
    limit: int = 10,
    session: Session | None = None
) -> List[DBMessage]:
    return session.query(DBMessage) \
        .filter(DBMessage.target == target) \
        .order_by(DBMessage.id.desc()) \
        .limit(limit) \
        .all()
