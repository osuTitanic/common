
from __future__ import annotations

from app.common.database.objects import DBGroup, DBGroupEntry, DBUser
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Iterable, List

from .wrapper import session_wrapper

@session_wrapper
def create_entry(
    user_id: int,
    group_id: int,
    session: Session = ...
) -> DBGroupEntry:
    session.add(
        ge := DBGroupEntry(
            user_id=user_id,
            group_id=group_id
        )
    )
    session.flush()
    return ge

@session_wrapper
def delete_entry(
    user_id: int,
    group_id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBGroupEntry) \
        .filter(DBGroupEntry.group_id == group_id) \
        .filter(DBGroupEntry.user_id == user_id) \
        .delete()
    session.flush()
    return rows

@session_wrapper
def entry_exists(
    user_id: int,
    group_id: int,
    session: Session = ...
) -> bool:
    return session.query(DBGroupEntry) \
        .filter(DBGroupEntry.group_id == group_id) \
        .filter(DBGroupEntry.user_id == user_id) \
        .count() > 0

@session_wrapper
def fetch_one(id: int, session: Session = ...) -> DBGroup | None:
    return session.query(DBGroup) \
        .filter(DBGroup.id == id) \
        .first()

@session_wrapper
def fetch_all(include_hidden: bool = False, session: Session = ...) -> List[DBGroup]:
    if include_hidden:
        return session.query(DBGroup) \
            .order_by(DBGroup.id.asc()) \
            .all()

    return session.query(DBGroup) \
        .filter(DBGroup.hidden == False) \
        .order_by(DBGroup.id.asc()) \
        .all()

@session_wrapper
def fetch_group_users(group_id: int, session: Session = ...) -> List[DBUser]:
    return session.query(DBUser) \
        .join(DBGroupEntry) \
        .filter(DBGroupEntry.group_id == group_id) \
        .order_by(DBUser.id.asc()) \
        .all()

@session_wrapper
def fetch_user_groups(
    user_id: int,
    include_hidden: bool = False,
    session: Session = ...
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
def fetch_by_users(
    user_ids: Iterable[int],
    include_hidden: bool = False,
    session: Session = ...
) -> Dict[int, List[DBGroup]]:
    user_ids = tuple(user_ids)

    if not user_ids:
        return {}

    query = session.query(
        DBGroupEntry.user_id,
        DBGroup
    ) \
        .join(DBGroup, DBGroup.id == DBGroupEntry.group_id) \
        .filter(DBGroupEntry.user_id.in_(user_ids))

    if not include_hidden:
        query = query.filter(DBGroup.hidden == False)

    rows = query \
        .order_by(DBGroupEntry.user_id.asc(), DBGroup.id.asc()) \
        .all()

    groups_by_user = {user_id: [] for user_id in user_ids}

    for user_id, group in rows:
        groups_by_user[user_id].append(group)

    return groups_by_user

@session_wrapper
def fetch_bancho_permissions(
    user_id: int,
    session: Session = ...
) -> int:
    return session.query(func.bit_or(DBGroup.bancho_permissions)) \
        .join(DBGroupEntry) \
        .filter(DBGroupEntry.user_id == user_id) \
        .scalar() or 0
