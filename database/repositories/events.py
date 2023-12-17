
from app.common.database.objects import DBMatchEvent
from app.common.constants import EventType
from typing import List, Optional

import app

def create(
    match_id: int,
    type: EventType,
    data: dict = {},
) -> DBMatchEvent:
    with app.session.database.managed_session() as session:
        session.add(
            m := DBMatchEvent(
                match_id,
                type.value,
                data
            )
        )
        session.commit()
        session.refresh(m)

    return m

def fetch_last(match_id: int) -> Optional[DBMatchEvent]:
    with app.session.database.managed_session() as session:
        return session.query(DBMatchEvent) \
            .filter(DBMatchEvent.match_id == match_id) \
            .order_by(DBMatchEvent.time.desc()) \
            .first()

def fetch_last_by_type(match_id: int, type: int) -> Optional[DBMatchEvent]:
    with app.session.database.managed_session() as session:
        return session.query(DBMatchEvent) \
            .filter(DBMatchEvent.match_id == match_id) \
            .filter(DBMatchEvent.type == type) \
            .order_by(DBMatchEvent.time.desc()) \
            .first()

def fetch_all(match_id: int) -> List[DBMatchEvent]:
    with app.session.database.managed_session() as session:
        return session.query(DBMatchEvent) \
            .filter(DBMatchEvent.match_id == match_id) \
            .all()

def delete_all(match_id: int) -> None:
    with app.session.database.managed_session() as session:
        session.query(DBMatchEvent) \
            .filter(DBMatchEvent.match_id == match_id) \
            .delete()
        session.commit()
