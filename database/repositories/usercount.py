
from __future__ import annotations

from app.common.database.objects import DBUserCount

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import desc, and_

from .wrapper import session_wrapper

@session_wrapper
def create(count: int, session: Session | None = None) -> DBUserCount:
    session.add(uc := DBUserCount(count))
    session.commit()
    return uc

@session_wrapper
def fetch_range(
    _until: datetime,
    _from: datetime,
    session: Session | None = None
) -> List[DBUserCount]:
    return session.query(DBUserCount) \
        .filter(and_(
            DBUserCount.time <= _from,
            DBUserCount.time >= _until
        )) \
        .order_by(desc(DBUserCount.time)) \
        .all()

@session_wrapper
def fetch_last(session: Session | None = None) -> Optional[DBUserCount]:
    return session.query(DBUserCount) \
        .order_by(desc(DBUserCount.time)) \
        .first()

@session_wrapper
def delete_old(
    delta: timedelta = timedelta(weeks=5),
    session: Session | None = None
) -> int:
    """Delete usercount entries that are older than the given delta (default ~1 month)"""
    rows = session.query(DBUserCount) \
            .filter(DBUserCount.time <= (datetime.now() - delta)) \
            .delete()
    session.commit()
    return rows
