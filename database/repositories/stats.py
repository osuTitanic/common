
from __future__ import annotations

from app.common.database.objects import (
    DBReplayHistory,
    DBBeatmap,
    DBStats,
    DBScore
)

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from .wrapper import session_wrapper
from . import scores

import config

@session_wrapper
def create(
    user_id: int,
    mode: int,
    session: Session = ...
) -> DBStats:
    session.add(
        stats := DBStats(
            user_id=user_id,
            mode=mode
        )
    )
    session.commit()
    session.refresh(stats)
    return stats

@session_wrapper
def update(
    user_id: int,
    mode: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBStats) \
           .filter(DBStats.user_id == user_id) \
           .filter(DBStats.mode == mode) \
           .update(updates)
    session.commit()
    return rows

@session_wrapper
def update_all(
    user_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBStats) \
           .filter(DBStats.user_id == user_id) \
           .update(updates)
    session.commit()
    return rows

@session_wrapper
def delete_all(user_id: int, session: Session = ...) -> int:
    rows = session.query(DBStats) \
            .filter(DBStats.user_id == user_id) \
            .delete()
    session.commit()
    return rows

@session_wrapper
def fetch_by_mode(
    user_id: int,
    mode: int,
    session: Session = ...
) -> DBStats | None:
    return session.query(DBStats) \
        .filter(DBStats.user_id == user_id) \
        .filter(DBStats.mode == mode) \
        .first()

@session_wrapper
def fetch_all(user_id: int, session: Session = ...) -> List[DBStats]:
    return session.query(DBStats) \
        .filter(DBStats.user_id == user_id) \
        .all()
