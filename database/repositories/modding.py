
from __future__ import annotations

from app.common.database.objects import DBBeatmapModding, DBForumPost
from typing import Dict, Iterable, List
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from .wrapper import session_wrapper

@session_wrapper
def create(
    target_id: int,
    sender_id: int,
    set_id: int,
    post_id: int,
    amount: int,
    session: Session = ...
) -> DBBeatmapModding:
    session.add(
        mod := DBBeatmapModding(
            target_id=target_id,
            sender_id=sender_id,
            set_id=set_id,
            post_id=post_id,
            amount=amount
        )
    )
    session.flush()
    session.refresh(mod)
    return mod

@session_wrapper
def fetch_one(
    id: int,
    session: Session = ...
) -> DBBeatmapModding | None:
    return session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.id == id) \
        .first()

@session_wrapper
def fetch_one_by_post(
    post_id: int,
    session: Session = ...
) -> DBBeatmapModding | None:
    return session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.post_id == post_id) \
        .order_by(DBBeatmapModding.id.desc()) \
        .first()

@session_wrapper
def fetch_by_post_and_sender(
    post_id: int,
    sender_id: int,
    session: Session = ...
) -> DBBeatmapModding | None:
    return session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.post_id == post_id) \
        .filter(DBBeatmapModding.sender_id == sender_id) \
        .first()

@session_wrapper
def fetch_all_by_post(
    post_id: int,
    session: Session = ...
) -> List[DBBeatmapModding]:
    return session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.post_id == post_id) \
        .all()

@session_wrapper
def fetch_all_by_target(
    target_id: int,
    session: Session = ...
) -> List[DBBeatmapModding]:
    return session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.target_id == target_id) \
        .all()

@session_wrapper
def fetch_all_by_sender(
    sender_id: int,
    session: Session = ...
) -> List[DBBeatmapModding]:
    return session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.sender_id == sender_id) \
        .all()

@session_wrapper
def fetch_all_by_set(
    set_id: int,
    session: Session = ...
) -> List[DBBeatmapModding]:
    return session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.set_id == set_id) \
        .all()

@session_wrapper
def total_amount(
    post_id: int,
    session: Session = ...
) -> int:
    return session.query(func.sum(DBBeatmapModding.amount)) \
        .filter(DBBeatmapModding.post_id == post_id) \
        .scalar() or 0

@session_wrapper
def fetch_total_kudosu_by_posts(
    post_ids: Iterable[int],
    session: Session = ...
) -> Dict[int, int]:
    if not post_ids:
        return {}

    rows = session.query(
        DBBeatmapModding.post_id,
        func.sum(DBBeatmapModding.amount)
    ) \
        .filter(DBBeatmapModding.post_id.in_(post_ids)) \
        .group_by(DBBeatmapModding.post_id) \
        .all()

    totals = {post_id: 0 for post_id in post_ids}

    for post_id, amount in rows:
        totals[post_id] = amount or 0

    return totals

@session_wrapper
def fetch_latest_by_posts(
    post_ids: Iterable[int],
    session: Session = ...
) -> Dict[int, DBBeatmapModding]:
    if not post_ids:
        return {}

    subquery = session.query(
        DBBeatmapModding.post_id.label('post_id'),
        func.max(DBBeatmapModding.id).label('max_id')
    ) \
        .filter(DBBeatmapModding.post_id.in_(post_ids)) \
        .group_by(DBBeatmapModding.post_id) \
        .subquery()

    rows = session.query(DBBeatmapModding) \
        .join(
            subquery,
            (DBBeatmapModding.post_id == subquery.c.post_id) &
            (DBBeatmapModding.id == subquery.c.max_id)
        ) \
        .all()

    return {row.post_id: row for row in rows}

@session_wrapper
def total_entries(
    post_id: int,
    session: Session = ...
) -> int:
    return session.query(func.count(DBBeatmapModding.id)) \
        .filter(DBBeatmapModding.post_id == post_id) \
        .scalar() or 0

@session_wrapper
def total_amount_by_user(
    user_id: int,
    session: Session = ...
) -> int:
    return session.query(func.sum(DBBeatmapModding.amount)) \
        .filter(DBBeatmapModding.target_id == user_id) \
        .scalar() or 0

@session_wrapper
def fetch_range_by_user(
    user_id: int,
    limit: int = 15,
    offset: int = 0,
    session: Session = ...
) -> List[DBBeatmapModding]:
    return session.query(DBBeatmapModding) \
        .filter(or_(
            DBBeatmapModding.target_id == user_id,
            DBBeatmapModding.sender_id == user_id
        )) \
        .order_by(DBBeatmapModding.id.desc()) \
        .offset(offset) \
        .limit(limit) \
        .all()

@session_wrapper
def update(
    id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.id == id) \
        .update(updates)
    session.flush()
    return rows

@session_wrapper
def delete(
    id: int,
    session: Session = ...
) -> None:
    session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.id == id) \
        .delete()
    session.flush()

@session_wrapper
def delete_by_post(
    post_id: int,
    session: Session = ...
) -> None:
    session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.post_id == post_id) \
        .delete()
    session.flush()

@session_wrapper
def delete_by_topic_id(
    topic_id: int,
    session: Session = ...
) -> None:
    session.query(DBBeatmapModding) \
        .join(DBForumPost, DBForumPost.id == DBBeatmapModding.post_id) \
        .filter(DBForumPost.topic_id == topic_id) \
        .delete()
    session.flush()

@session_wrapper
def delete_by_set_id(
    set_id: int,
    session: Session = ...
) -> None:
    session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.set_id == set_id) \
        .delete()
    session.flush()
