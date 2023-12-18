
from __future__ import annotations

from app.common.database.objects import DBChannel
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    name: str,
    topic: str,
    read_permissions: int,
    write_permissions: int,
    session: Session | None = None
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
def fetch_all(session: Session | None = None) -> List[DBChannel]:
    return session.query(DBChannel) \
                  .all()
