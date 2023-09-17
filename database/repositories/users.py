
from app.common.database.objects import DBUser, DBStats
from typing import Optional, List

import app

def create(
    username: str,
    email: str,
    pw_bcrypt: str,
    country: str
) -> DBUser:
    with app.session.database.managed_session() as session:
        session.add(
            user := DBUser(
                username,
                email,
                pw_bcrypt,
                country
            )
        )
        session.commit()
        session.refresh(user)

    return user

def update(user_id: int, updates: dict) -> int:
    with app.session.database.managed_session() as session:
        rows = session.query(DBUser) \
               .filter(DBUser.id == user_id) \
               .update(updates)
        session.commit()

    return rows

def fetch_by_name(username: str) -> Optional[DBUser]:
    return app.session.database.session.query(DBUser) \
        .filter(DBUser.name == username) \
        .first()

def fetch_by_id(id: int) -> Optional[DBUser]:
    return app.session.database.session.query(DBUser) \
        .filter(DBUser.id == id) \
        .first()

def fetch_active() -> List[DBUser]:
    return app.session.database.session.query(DBUser) \
        .join(DBStats) \
        .filter(DBUser.restricted == False) \
        .filter(DBStats.playcount > 0) \
        .all()

def fetch_by_discord_id(id: int) -> Optional[DBUser]:
    return app.session.database.session.query(DBUser) \
        .filter(DBUser.discord_id == id) \
        .first()
