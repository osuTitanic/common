
from app.common.database.objects import DBUser, DBStats
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_

from ...helpers.caching import ttl_cache

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

def fetch_by_email(email: str) -> Optional[DBUser]:
    return app.session.database.session.query(DBUser) \
        .filter(DBUser.email == email) \
        .first()

def fetch_all(restricted: bool = False) -> List[DBUser]:
    return app.session.database.session.query(DBUser) \
        .filter(DBUser.restricted == restricted) \
        .all()

def fetch_active(delta: timedelta = timedelta(days=30), *preload) -> List[DBUser]:
    return app.session.database.session.query(DBUser) \
        .join(DBStats) \
        .options(selectinload(*preload)) \
        .filter(DBUser.restricted == False) \
        .filter(DBStats.playcount > 0) \
        .filter(
            # Remove inactive users from query, if they are not in the top 100
            or_(
                DBUser.latest_activity >= (datetime.now() - delta),
                DBStats.rank >= 100
            )
        ) \
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

@ttl_cache(ttl=10*60)
def fetch_many(user_ids: tuple, *options) -> List[DBUser]:
    return app.session.database.session.query(DBUser) \
              .options(*[selectinload(item) for item in options]) \
              .filter(DBUser.id.in_(user_ids)) \
              .all()
