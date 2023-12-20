
from __future__ import annotations

from app.common.database.objects import DBGroup, DBGroupEntry, DBUser
from sqlalchemy.orm import Session, selectinload
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def fetch_one(id: int, session: Session | None = None) -> DBGroup | None:
    return session.query(DBGroup) \
        .filter(DBGroup.id == id) \
        .first()

@session_wrapper
def fetch_user_groups(user_id: int, session: Session | None = None) -> List[DBGroup]:
    return session.query(DBGroup) \
        .join(DBGroupEntry) \
        .filter(DBGroupEntry.user_id == user_id) \
        .all()

@session_wrapper
def fetch_group_users(group_id: int, session: Session | None = None) -> List[DBUser]:
    return session.query(DBUser) \
        .join(DBGroupEntry) \
        .filter(DBGroupEntry.group_id == group_id) \
        .all()
