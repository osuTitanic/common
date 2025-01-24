
from __future__ import annotations

from app.common.database.objects import DBChannel, DBMessage
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    name: str,
    topic: str,
    read_permissions: int,
    write_permissions: int,
    session: Session = ...
) -> DBChannel:
    session.add(
        chan := DBChannel(
            name,
            topic,
            read_permissions,
            write_permissions
        )
    )
    session.commit()
    return chan

@session_wrapper
def fetch_all(session: Session = ...) -> List[DBChannel]:
    return session.query(DBChannel) \
        .all()

@session_wrapper
def fetch_one(
    name: str,
    session: Session = ...
) -> DBChannel:
    return session.query(DBChannel) \
        .filter(DBChannel.name == name) \
        .first()

@session_wrapper
def fetch_by_permissions(
    read_permissions: int,
    session: Session = ...
) -> List[DBChannel]:
    return session.query(DBChannel) \
        .filter(DBChannel.read_permissions < read_permissions) \
        .all()

@session_wrapper
def fetch_channel_entries(
    username: str,
    session: Session = ...
) -> List[DBChannel]:
    channel_names = session.query(DBMessage.target) \
        .filter(DBMessage.sender == username) \
        .filter(DBMessage.target.ilike('#%')) \
        .distinct() \
        .all()

    return session.query(DBChannel) \
        .filter(DBChannel.name.in_([name for name, in channel_names])) \
        .all()
