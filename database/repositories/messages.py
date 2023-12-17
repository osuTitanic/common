
from app.common.database.objects import DBMessage
from typing import List

import app

def create(
    sender: str,
    target: str,
    message: str
) -> DBMessage:
    with app.session.database.managed_session() as session:
        session.add(
            msg := DBMessage(
                sender,
                target,
                message
            )
        )
        session.commit()
        session.refresh(msg)

    return msg

def fetch_recent(target: str = '#osu', limit: int = 10) -> List[DBMessage]:
    with app.session.database.managed_session() as session:
        return session.query(DBMessage) \
            .filter(DBMessage.target == target) \
            .order_by(DBMessage.id.desc()) \
            .limit(limit) \
            .all()
