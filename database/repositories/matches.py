
from app.common.database.repositories import events
from app.common.database.objects import DBMatch

from typing import Optional

import app

def create(
    name: str,
    bancho_id: int,
    creator_id: int,
) -> DBMatch:
    with app.session.database.managed_session() as session:
        session.add(
            m := DBMatch(
                name,
                creator_id,
                bancho_id
            )
        )
        session.commit()
        session.refresh(m)

    return m

def fetch_by_id(id: int) -> Optional[DBMatch]:
    with app.session.database.managed_session() as session:
        return session.query(DBMatch) \
            .filter(DBMatch.id == id) \
            .first()

def fetch_by_bancho_id(id: int) -> Optional[DBMatch]:
    with app.session.database.managed_session() as session:
        return session.query(DBMatch) \
            .filter(DBMatch.bancho_id == id) \
            .first()

def update(id: int, updates: dict) -> None:
    with app.session.database.managed_session() as session:
        session.query(DBMatch) \
            .filter(DBMatch.id == id) \
            .update(updates)
        session.commit()

def delete(id: int) -> None:
    # Delete events first
    events.delete_all(id)

    with app.session.database.managed_session() as session:
        session.query(DBMatch) \
            .filter(DBMatch.id == id) \
            .delete()
        session.commit()
