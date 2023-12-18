
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
    session: Session | None = None
) -> DBComment:
    session.add(
        c := DBComment(
            target_id,
            target,
            user_id,
            time,
            content,
            comment_format,
            playmode,
            color
        )
    )
    session.commit()
    session.refresh(c)
    return c

@session_wrapper
def fetch_many(
    target_id: int,
    type: str,
    session: Session | None = None
) -> List[DBComment]:
    return session.query(DBComment) \
        .filter(DBComment.target_id == target_id) \
        .filter(DBComment.target_type == type) \
        .order_by(DBComment.time.asc()) \
        .all()
