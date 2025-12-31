
from __future__ import annotations

from app.common.database.objects import DBReleaseChangelog
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def fetch_one(id: int, session: Session = ...) -> DBReleaseChangelog | None:
    return session.query(DBReleaseChangelog) \
        .filter(DBReleaseChangelog.id == id) \
        .first()

@session_wrapper
def fetch_range_asc(
    start_date: datetime,
    limit: int = 100,
    offset: int = 0,
    session: Session = ...
) -> List[DBReleaseChangelog]:
    return session.query(DBReleaseChangelog) \
        .filter(DBReleaseChangelog.created_at >= start_date) \
        .order_by(DBReleaseChangelog.created_at.asc()) \
        .offset(offset) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_range_desc(
    start_date: datetime,
    limit: int = 100,
    offset: int = 0,
    session: Session = ...
) -> List[DBReleaseChangelog]:
    return session.query(DBReleaseChangelog) \
        .filter(DBReleaseChangelog.created_at <= start_date) \
        .order_by(DBReleaseChangelog.created_at.desc()) \
        .offset(offset) \
        .limit(limit) \
        .all()
