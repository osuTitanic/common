
from app.common.database.objects import DBUser, DBStats
from sqlalchemy import func, or_, and_
from typing import Optional, List

import app

def create(
    username: str,
    safe_name: str,
    email: str,
    pw_bcrypt: str,
    country: str,
    activated: bool = False,
    discord_id: Optional[int] = None,
    permissions: int = 1
) -> Optional[DBUser]:
    with app.session.database.managed_session() as session:
        session.add(
            user := DBUser(
                username,
                safe_name,
                email,
                pw_bcrypt,
                country,
                activated,
                discord_id,
                permissions
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

def fetch_by_name_extended(query: str) -> Optional[DBUser]:
    """Used for searching users"""
    return app.session.database.session.query(DBUser) \
        .filter(or_(
            DBUser.name.ilike(query),
            DBUser.name.ilike(f'%{query}%')
        )) \
        .order_by(func.length(DBUser.name).asc()) \
        .first()

def fetch_by_safe_name(username: str) -> Optional[DBUser]:
    return app.session.database.session.query(DBUser) \
        .filter(DBUser.safe_name == username) \
        .first()

def fetch_by_id(id: int) -> Optional[DBUser]:
    return app.session.database.session.query(DBUser) \
        .filter(DBUser.id == id) \
        .first()

def fetch_all(restricted: bool = False) -> List[DBUser]:
    return app.session.database.session.query(DBUser) \
        .filter(DBUser.restricted == restricted) \
        .all()

def fetch_by_discord_id(id: int) -> Optional[DBUser]:
    return app.session.database.session.query(DBUser) \
        .filter(DBUser.discord_id == id) \
        .first()

def fetch_count(exclude_restricted=True) -> int:
    query = app.session.database.session.query(
        func.count(DBUser.id)
    )

    if exclude_restricted:
        query = query.filter(DBUser.restricted == False)

    return query.scalar()
