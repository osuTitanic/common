
from __future__ import annotations
from typing import List

from datetime import datetime, timedelta
from app.common.database.objects import (
    DBForumSubscriber,
    DBForumBookmark,
    DBForumPost,
    DBStats,
    DBUser
)

from sqlalchemy.orm import selectinload, joinedload, Session
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
    discord_id: int | None = None,
    session: Session = ...
) -> DBUser | None:
    session.add(
        user := DBUser(
            username,
            safe_name,
            email,
            pw_bcrypt,
            country,
            activated,
            discord_id
        )
    )
    session.commit()
    session.refresh(user)
    return user

@session_wrapper
def update(
    user_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBUser) \
           .filter(DBUser.id == user_id) \
           .update(updates)
    session.commit()
    return rows

@session_wrapper
def fetch_by_name(username: str, session: Session = ...) -> DBUser | None:
    return session.query(DBUser) \
        .filter(DBUser.name == username) \
        .first()

@session_wrapper
def fetch_by_name_case_insensitive(username: str, session: Session = ...) -> DBUser | None:
    return session.query(DBUser) \
        .filter(func.lower(DBUser.name) == username.lower()) \
        .first()

@session_wrapper
def fetch_by_name_extended(query: str, session: Session = ...) -> DBUser | None:
    """Used for searching users"""
    return session.query(DBUser) \
        .filter(or_(
            func.lower(DBUser.name) == query.lower(),
            DBUser.name.ilike(f'%{query}%')
        )) \
        .order_by(func.length(DBUser.name).asc()) \
        .first()

@session_wrapper
def fetch_by_safe_name(username: str, session: Session = ...) -> DBUser | None:
    return session.query(DBUser) \
        .filter(DBUser.safe_name == username) \
        .first()

@session_wrapper
def fetch_by_id(id: int, *options, session: Session = ...) -> DBUser | None:
    return session.query(DBUser) \
        .options(*[selectinload(item) for item in options]) \
        .filter(DBUser.id == id) \
        .first()

@session_wrapper
def fetch_by_id_no_options(id: int, session: Session = ...) -> DBUser | None:
    return session.query(DBUser) \
        .filter(DBUser.id == id) \
        .first()

@session_wrapper
def fetch_by_email(email: str, session: Session = ...) -> DBUser | None:
    return session.query(DBUser) \
        .filter(DBUser.email == email) \
        .first()

@session_wrapper
def fetch_all(restricted: bool = False, session: Session = ...) -> List[DBUser]:
    return session.query(DBUser) \
        .filter(DBUser.restricted == restricted) \
        .all()

@session_wrapper
def fetch_active(delta: timedelta = timedelta(days=30), session: Session = ...) -> List[DBUser]:
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
def fetch_by_discord_id(id: int, session: Session = ...) -> DBUser | None:
    return session.query(DBUser) \
        .filter(DBUser.discord_id == id) \
        .first()

@session_wrapper
def fetch_count(exclude_restricted=True, session: Session = ...) -> int:
    query = session.query(
        func.count(DBUser.id)
    )

    if exclude_restricted:
        query = query.filter(DBUser.restricted == False)

    return query.scalar()

@session_wrapper
def fetch_username(user_id: int, session: Session = ...) -> str | None:
    return session.query(DBUser.name) \
            .filter(DBUser.id == user_id) \
            .scalar()

@session_wrapper
def fetch_irc_token(safe_name: str, session: Session = ...) -> str | None:
    return session.query(DBUser.irc_token) \
            .filter(DBUser.safe_name == safe_name) \
            .scalar()

@session_wrapper
def fetch_user_id(username: str, session: Session = ...) -> int | None:
    return session.query(DBUser.id) \
            .filter(DBUser.name == username) \
            .scalar()

@session_wrapper
def fetch_many(user_ids: list, *options, session: Session = ...) -> List[DBUser]:
    return session.query(DBUser) \
              .options(*[joinedload(item) for item in options]) \
              .filter(DBUser.id.in_(user_ids)) \
              .all()

@session_wrapper
def fetch_top(limit: int = 50, session: Session = ...) -> List[DBUser]:
    return session.query(DBUser) \
        .join(DBStats) \
        .filter(DBUser.restricted == False) \
        .order_by(DBStats.rank.asc()) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_recent(limit: int = 50, session: Session = ...) -> List[DBUser]:
    return session.query(DBUser) \
        .filter(DBUser.restricted == False) \
        .filter(DBUser.activated == True) \
        .order_by(DBUser.created_at.desc()) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_post_count(user_id: int, session: Session = ...) -> int:
    return session.query(DBForumPost) \
        .filter(DBForumPost.user_id == user_id) \
        .count()

@session_wrapper
def fetch_subscriptions(user_id: int, session: Session = ...) -> List[DBForumSubscriber]:
    return session.query(DBForumSubscriber) \
        .filter(DBForumSubscriber.user_id == user_id) \
        .all()

@session_wrapper
def fetch_bookmarks(user_id: int, session: Session = ...) -> List[DBForumBookmark]:
    return session.query(DBForumBookmark) \
        .filter(DBForumBookmark.user_id == user_id) \
        .all()
