
from __future__ import annotations

from app.common.database.objects import DBActivity
from app.common.constants import UserActivity
from datetime import datetime, timedelta
from typing import List, Iterable
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    mode: int | None,
    type: UserActivity,
    data: dict,
    hidden: bool = False,
    session: Session = ...
) -> DBActivity:
    session.add(
        ac := DBActivity(
            user_id=user_id,
            mode=mode,
            type=type,
            data=data,
            hidden=hidden,
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
    excluded_types: Iterable[UserActivity] = (),
    session: Session = ...
) -> List[DBActivity]:
    query = session.query(DBActivity) \
        .filter(or_(DBActivity.mode == mode, DBActivity.mode == None)) \
        .filter(DBActivity.time > datetime.now() - until) \
        .filter(DBActivity.user_id == user_id) \
        .filter(DBActivity.hidden == False) \
        .order_by(DBActivity.id.desc())

    if excluded_types:
        excluded = DBActivity.type.notin_([t.value for t in excluded_types])
        query = query.filter(excluded)

    return query.all()
