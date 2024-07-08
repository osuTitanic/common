
from __future__ import annotations

from app.common.database.objects import DBBeatmapModding
from sqlalchemy.orm import Session
from typing import List

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
    session.commit()
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
def update(
    id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.id == id) \
        .update(updates)
    session.commit()
    return rows

@session_wrapper
def delete(
    id: int,
    session: Session = ...
) -> None:
    session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.id == id) \
        .delete()
    session.commit()

@session_wrapper
def delete_by_post(
    post_id: int,
    session: Session = ...
) -> None:
    session.query(DBBeatmapModding) \
        .filter(DBBeatmapModding.post_id == post_id) \
        .delete()
    session.commit()
