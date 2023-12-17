
from app.common.database.objects import DBComment
from typing import List

import app

def create(
    target_id: int,
    target: str,
    user_id: int,
    time: int,
    content: str,
    comment_format: str,
    playmode: int,
    color: str
) -> DBComment:
    with app.session.database.managed_session() as session:
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

def fetch_many(target_id: int, type: str) -> List[DBComment]:
    with app.session.database.managed_session() as session:
        return session.query(DBComment) \
            .filter(DBComment.target_id == target_id) \
            .filter(DBComment.target_type == type) \
            .order_by(DBComment.time.asc()) \
            .all()
