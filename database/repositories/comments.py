
from __future__ import annotations

from app.common.database.objects import DBComment
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    target_id: int,
    target: str,
    user_id: int,
    time: int,
    content: str,
    comment_format: str,
    playmode: int,
    color: str,
    session: Session = ...
) -> DBComment:
    session.add(
        c := DBComment(
            target_id=target_id,
            target_type=target,
            user_id=user_id,
            time=time,
            comment=content,
            format=comment_format,
            mode=playmode,
            color=color
        )
    )
    session.commit()
    session.refresh(c)
    return c

@session_wrapper
def fetch_many(
    target_id: int,
    type: str,
    session: Session = ...
) -> List[DBComment]:
    return session.query(DBComment) \
        .filter(DBComment.target_id == target_id) \
        .filter(DBComment.target_type == type) \
        .order_by(DBComment.time.asc()) \
        .all()
