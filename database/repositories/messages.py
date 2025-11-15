
from __future__ import annotations

from app.common.database.objects import DBUser, DBMessage, DBDirectMessage
from sqlalchemy import or_, case, func
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict

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
            sender=sender,
            target=target,
            message=message,
            time=datetime.now()
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
    read: bool = True,
    session: Session = ...
) -> DBDirectMessage:
    session.add(
        msg := DBDirectMessage(
            time=datetime.now(),
            sender_id=sender_id,
            target_id=target_id,
            message=message,
            read=read
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
def fetch_dm(message_id: int, session: Session = ...) -> DBDirectMessage | None:
    return session.query(DBDirectMessage) \
        .filter(DBDirectMessage.id == message_id) \
        .first()

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

@session_wrapper
def fetch_dms_unread_count(
    user_id: int,
    target_id: int,
    session: Session = ...
) -> int:
    count = session.query(DBDirectMessage) \
        .filter(DBDirectMessage.target_id == target_id) \
        .filter(DBDirectMessage.sender_id == user_id) \
        .filter(DBDirectMessage.read == False) \
        .count()
    return count or 0

@session_wrapper
def fetch_dms_unread_count_all(
    user_id: int,
    session: Session = ...
) -> Dict[int, int]:
    results = session.query(
        DBDirectMessage.sender_id,
        func.count(DBDirectMessage.id)
    ) \
        .filter(DBDirectMessage.target_id == user_id) \
        .filter(DBDirectMessage.read == False) \
        .group_by(DBDirectMessage.sender_id) \
        .all()

    return {sender_id: count for sender_id, count in results}

@session_wrapper
def fetch_dm_entries(
    user_id: int,
    session: Session = ...
) -> List[DBUser]:
    return session.query(DBUser) \
        .join(DBDirectMessage, case(
            (DBDirectMessage.sender_id == user_id, DBDirectMessage.target_id),
            else_=DBDirectMessage.sender_id
        ) == DBUser.id) \
        .filter(or_(
            DBDirectMessage.sender_id == user_id,
            DBDirectMessage.target_id == user_id
        )) \
        .distinct(DBUser.id) \
        .all()

@session_wrapper
def fetch_last_dm(
    sender_id: int,
    target_id: int,
    session: Session = ...
) -> DBDirectMessage | None:
    return session.query(DBDirectMessage) \
        .filter(or_(
            (DBDirectMessage.sender_id == sender_id) & (DBDirectMessage.target_id == target_id),
            (DBDirectMessage.sender_id == target_id) & (DBDirectMessage.target_id == sender_id)
        )) \
        .order_by(DBDirectMessage.id.desc()) \
        .first()

@session_wrapper
def update(
    message_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    result = session.query(DBDirectMessage) \
        .filter(DBDirectMessage.id == message_id) \
        .update(updates)
    session.commit()
    return result

@session_wrapper
def update_private(
    message_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    result = session.query(DBDirectMessage) \
        .filter(DBDirectMessage.id == message_id) \
        .update(updates)
    session.commit()
    return result

@session_wrapper
def update_private_all(
    sender_id: int,
    target_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    result = session.query(DBDirectMessage) \
        .filter(DBDirectMessage.sender_id == sender_id) \
        .filter(DBDirectMessage.target_id == target_id) \
        .update(updates, synchronize_session=False)
    session.commit()
    return result
