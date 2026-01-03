
from __future__ import annotations

from app.common.database.objects import DBFavourite
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    set_id: int,
    session: Session = ...
) -> DBFavourite | None:
    # Check if favourite was already set
    if session.query(DBFavourite.user_id) \
        .filter(DBFavourite.user_id == user_id) \
        .filter(DBFavourite.set_id == set_id) \
        .first():
        return None

    session.add(
        fav := DBFavourite(
            user_id=user_id,
            set_id=set_id
        )
    )
    session.flush()

    return fav

@session_wrapper
def fetch_one(
    user_id: int,
    set_id: int,
    session: Session = ...
) -> DBFavourite | None:
    return session.query(DBFavourite) \
        .filter(DBFavourite.user_id == user_id) \
        .filter(DBFavourite.set_id == set_id) \
        .first()

@session_wrapper
def fetch_many(user_id: int, session: Session = ...) -> List[DBFavourite]:
    return session.query(DBFavourite) \
        .filter(DBFavourite.user_id == user_id) \
        .all()

@session_wrapper
def fetch_many_by_set(set_id: int, limit: int = 5, session: Session = ...) -> List[DBFavourite]:
    return session.query(DBFavourite) \
        .filter(DBFavourite.set_id == set_id) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_count(user_id: int, session: Session = ...) -> int:
    return session.query(DBFavourite) \
        .filter(DBFavourite.user_id == user_id) \
        .count()

@session_wrapper
def fetch_count_by_set(set_id: int, session: Session = ...) -> int:
    return session.query(DBFavourite) \
        .filter(DBFavourite.set_id == set_id) \
        .count()

@session_wrapper
def delete(
    user_id: int,
    set_id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBFavourite) \
        .filter(DBFavourite.user_id == user_id) \
        .filter(DBFavourite.set_id == set_id) \
        .delete()
    session.flush()
    return rows

@session_wrapper
def delete_all(set_id: int, session: Session = ...) -> int:
    rows = session.query(DBFavourite) \
        .filter(DBFavourite.set_id == set_id) \
        .delete()
    session.flush()
    return rows
