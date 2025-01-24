
from __future__ import annotations

from app.common.database.objects import DBMessage, DBDirectMessage
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    sender: str,
    target: str,
    message: str,
    session: Session = ...
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
def create_private(
    sender_id: int,
    target_id: int,
    message: str,
    session: Session = ...
) -> DBDirectMessage:
    session.add(
        msg := DBDirectMessage(
            sender_id,
            target_id,
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
    offset: int = 0,
    session: Session = ...
) -> List[DBMessage]:
    return session.query(DBMessage) \
        .filter(DBMessage.target == target) \
        .order_by(DBMessage.id.desc()) \
        .offset(offset) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_dms(
    sender_id: int,
    target_id: int,
    limit: int = 10,
    offset: int = 0,
    session: Session = ...
) -> List[DBDirectMessage]:
    return session.query(DBDirectMessage) \
        .filter(or_(
            (DBDirectMessage.sender_id == sender_id) & (DBDirectMessage.target_id == target_id),
            (DBDirectMessage.sender_id == target_id) & (DBDirectMessage.target_id == sender_id)
        )) \
        .order_by(DBDirectMessage.id.desc()) \
        .offset(offset) \
        .limit(limit) \
        .all()
