
from __future__ import annotations

from app.common.database.objects import DBGroup, DBGroupEntry, DBUser
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create_entry(
    user_id: int,
    group_id: int,
    session: Session | None = None
) -> DBGroupEntry:
    session.add(
        ge := DBGroupEntry(
            user_id,
            group_id
        )
    )
    session.commit()
    return ge

@session_wrapper
def delete_entry(
    user_id: int,
    group_id: int,
    session: Session | None = None
) -> int:
    return session.query(DBGroupEntry) \
        .filter(DBGroupEntry.group_id == group_id) \
        .filter(DBGroupEntry.user_id == user_id) \
        .delete()

@session_wrapper
def fetch_one(id: int, session: Session | None = None) -> DBGroup | None:
    return session.query(DBGroup) \
        .filter(DBGroup.id == id) \
        .first()

@session_wrapper
def fetch_all(include_hidden: bool = False, session: Session | None = None) -> List[DBGroup]:
    if include_hidden:
        return session.query(DBGroup) \
            .order_by(DBGroup.id.asc()) \
            .all()

    return session.query(DBGroup) \
        .filter(DBGroup.hidden == False) \
        .order_by(DBGroup.id.asc()) \
        .all()

@session_wrapper
def fetch_group_users(group_id: int, session: Session | None = None) -> List[DBUser]:
    return session.query(DBUser) \
        .join(DBGroupEntry) \
        .filter(DBGroupEntry.group_id == group_id) \
        .order_by(DBUser.id.asc()) \
        .all()

@session_wrapper
def fetch_user_groups(
    user_id: int,
    include_hidden: bool = False,
    session: Session | None = None
) -> List[DBGroup]:
    if include_hidden:
        return session.query(DBGroup) \
            .join(DBGroupEntry) \
            .filter(DBGroupEntry.user_id == user_id) \
            .order_by(DBGroup.id.asc()) \
            .all()

    return session.query(DBGroup) \
        .join(DBGroupEntry) \
        .filter(DBGroupEntry.user_id == user_id) \
        .filter(DBGroup.hidden == False) \
        .order_by(DBGroup.id.asc()) \
        .all()

@session_wrapper
def get_player_permissions(
    user_id: int,
    session: Session | None = None
) -> int:
    return session.query(func.sum(DBGroup.bancho_permissions)) \
        .join(DBGroupEntry) \
        .filter(DBGroupEntry.user_id == user_id) \
        .scalar() or 0
