
from __future__ import annotations

from app.common.database.objects import DBUserActivity

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    osu_count: int,
    irc_count: int,
    mp_count: int,
    session: Session = ...
) -> DBUserActivity:
    session.add(uc := DBUserActivity(
        osu_count=osu_count,
        irc_count=irc_count,
        mp_count=mp_count,
        time=datetime.now()
    ))
    session.commit()
    return uc

@session_wrapper
def fetch_range(
    _until: datetime,
    _from: datetime,
    session: Session = ...
) -> List[DBUserActivity]:
    return session.query(DBUserActivity) \
        .filter(and_(
            DBUserActivity.time <= _from,
            DBUserActivity.time >= _until
        )) \
        .order_by(desc(DBUserActivity.time)) \
        .all()

@session_wrapper
def fetch_last(session: Session = ...) -> DBUserActivity | None:
    return session.query(DBUserActivity) \
        .order_by(desc(DBUserActivity.time)) \
        .first()

@session_wrapper
def delete_old(
    delta: timedelta = timedelta(weeks=5),
    session: Session = ...
) -> int:
    """Delete usercount entries that are older than the given delta (default ~1 month)"""
    rows = session.query(DBUserActivity) \
            .filter(DBUserActivity.time <= (datetime.now() - delta)) \
            .delete()
    session.commit()
    return rows
