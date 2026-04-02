
from app.common.database.objects import DBChannel, DBMessage
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper, SessionProvider

@session_wrapper
def create(
    name: str,
    topic: str,
    read_permissions: int,
    write_permissions: int,
    session: Session = SessionProvider
) -> DBChannel:
    session.add(
        chan := DBChannel(
            name=name,
            topic=topic,
            read_permissions=read_permissions,
            write_permissions=write_permissions
        )
    )
    session.flush()
    return chan

@session_wrapper
def fetch_all(session: Session = SessionProvider) -> List[DBChannel]:
    return session.query(DBChannel) \
        .all()

@session_wrapper
def fetch_one(
    name: str,
    session: Session = SessionProvider
) -> DBChannel:
    return session.query(DBChannel) \
        .filter(DBChannel.name == name) \
        .first()

@session_wrapper
def fetch_by_permissions(
    read_permissions: int,
    session: Session = SessionProvider
) -> List[DBChannel]:
    return session.query(DBChannel) \
        .filter(DBChannel.read_permissions < read_permissions) \
        .all()

@session_wrapper
def fetch_channel_entries(
    username: str,
    session: Session = SessionProvider
) -> List[DBChannel]:
    channel_names = session.query(DBMessage.target) \
        .filter(DBMessage.sender == username) \
        .filter(DBMessage.target.ilike('#%')) \
        .distinct() \
        .all()

    return session.query(DBChannel) \
        .filter(DBChannel.name.in_([name for name, in channel_names])) \
        .all()
