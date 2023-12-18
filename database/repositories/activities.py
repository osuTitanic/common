
from __future__ import annotations

from app.common.database.objects import DBActivity
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    mode: int,
    text: str,
    args: str,
    links: str,
    session: Session | None = None
) -> DBActivity:
    session.add(
        ac := DBActivity(
            user_id,
            mode,
            text,
            args,
            links
        )
    )
    session.commit()
    session.refresh(ac)
    return ac

@session_wrapper
def fetch_recent(
    user_id: int,
    mode: int,
    until: timedelta = timedelta(days=30),
    session: Session | None = None
) -> List[DBActivity]:
    return session.query(DBActivity) \
        .filter(DBActivity.time > datetime.now() - until) \
        .filter(DBActivity.user_id == user_id) \
        .filter(DBActivity.mode == mode) \
        .order_by(DBActivity.id.desc()) \
        .all()
