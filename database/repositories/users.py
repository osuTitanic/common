
from __future__ import annotations

from app.common.database.objects import DBUser, DBStats
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.orm import selectinload, Session
from sqlalchemy import func, or_

from .wrapper import session_wrapper

@session_wrapper
def create(
    username: str,
    safe_name: str,
    email: str,
    pw_bcrypt: str,
    country: str,
    activated: bool = False,
    discord_id: Optional[int] = None,
    permissions: int = 1,
    session: Session | None = None
) -> Optional[DBUser]:
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

@session_wrapper
def update(
    user_id: int,
    updates: dict,
    session: Session | None = None
) -> int:
    rows = session.query(DBUser) \
           .filter(DBUser.id == user_id) \
           .update(updates)
    session.commit()
    return rows

@session_wrapper
def fetch_by_name(username: str, session: Session | None = None) -> Optional[DBUser]:
    return session.query(DBUser) \
        .filter(DBUser.name == username) \
        .first()

@session_wrapper
def fetch_by_name_extended(query: str, session: Session | None = None) -> Optional[DBUser]:
    """Used for searching users"""
    return session.query(DBUser) \
        .filter(or_(
            DBUser.name.ilike(query),
            DBUser.name.ilike(f'%{query}%')
        )) \
        .order_by(func.length(DBUser.name).asc()) \
        .first()

@session_wrapper
def fetch_by_safe_name(username: str, session: Session | None = None) -> Optional[DBUser]:
    return session.query(DBUser) \
        .filter(DBUser.safe_name == username) \
        .first()

@session_wrapper
def fetch_by_id(id: int, session: Session | None = None) -> Optional[DBUser]:
    return session.query(DBUser) \
        .filter(DBUser.id == id) \
        .first()

@session_wrapper
def fetch_by_email(email: str, session: Session | None = None) -> Optional[DBUser]:
    return session.query(DBUser) \
        .filter(DBUser.email == email) \
        .first()

@session_wrapper
def fetch_all(restricted: bool = False, session: Session | None = None) -> List[DBUser]:
    return session.query(DBUser) \
        .filter(DBUser.restricted == restricted) \
        .all()

@session_wrapper
def fetch_active(delta: timedelta = timedelta(days=30), session: Session | None = None) -> List[DBUser]:
    return session.query(DBUser) \
        .join(DBStats) \
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

@session_wrapper
def fetch_by_discord_id(id: int, session: Session | None = None) -> Optional[DBUser]:
    return session.query(DBUser) \
        .filter(DBUser.discord_id == id) \
        .first()

@session_wrapper
def fetch_count(exclude_restricted=True, session: Session | None = None) -> int:
    query = session.query(
        func.count(DBUser.id)
    )

    if exclude_restricted:
        query = query.filter(DBUser.restricted == False)

    return query.scalar()

@session_wrapper
def fetch_username(user_id: int, session: Session | None = None) -> Optional[str]:
    return session.query(DBUser.name) \
            .filter(DBUser.id == user_id) \
            .scalar()

@session_wrapper
def fetch_user_id(username: str, session: Session | None = None) -> Optional[int]:
    return session.query(DBUser.id) \
            .filter(DBUser.name == username) \
            .scalar()

@session_wrapper
def fetch_many(user_ids: tuple, *options, session: Session | None = None) -> List[DBUser]:
    return session.query(DBUser) \
              .options(*[selectinload(item) for item in options]) \
              .filter(DBUser.id.in_(user_ids)) \
              .all()
