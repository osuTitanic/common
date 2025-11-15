
from __future__ import annotations

from app.common.database.objects import DBName, DBUser
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(user_id: int, old_name: str, session: Session = ...) -> DBName:
    session.add(
        name := DBName(
            user_id=user_id,
            name=old_name,
            changed_at=datetime.now()
        )
    )
    session.commit()
    return name

@session_wrapper
def fetch_one(id: int, session: Session = ...) -> DBName:
    return session.query(DBName) \
        .filter(DBName.id == id) \
        .first()

@session_wrapper
def fetch_all(user_id: int, session: Session = ...) -> List[DBName]:
    return session.query(DBName) \
        .filter(DBName.user_id == user_id) \
        .all()

@session_wrapper
def fetch_all_reserved(user_id: int, session: Session = ...) -> List[DBName]:
    return session.query(DBName) \
        .filter(DBName.user_id == user_id) \
        .filter(DBName.reserved == True) \
        .all()

@session_wrapper
def fetch_by_name(name: str, session: Session = ...) -> DBName | None:
    return session.query(DBName) \
        .filter(DBName.name == name) \
        .first()

@session_wrapper
def fetch_by_name_extended(name: str, session: Session = ...) -> DBName | None:
    return session.query(DBName) \
        .filter(or_(
            DBName.name.ilike(name),
            DBName.name.ilike(f'%{name}%')
        )) \
        .order_by(func.length(DBName.name).asc()) \
        .first()

@session_wrapper
def fetch_user_by_past_name(name: str, session: Session = ...) -> DBUser | None:
    return session.query(DBUser) \
        .join(DBName, DBUser.id == DBName.user_id) \
        .filter(DBName.name.ilike(name)) \
        .first()

@session_wrapper
def fetch_by_name_reserved(name: str, session: Session = ...) -> DBName | None:
    return session.query(DBName) \
        .filter(DBName.name.ilike(name)) \
        .filter(DBName.reserved == True) \
        .order_by(func.length(DBName.name).asc()) \
        .first()

@session_wrapper
def update(
    id: int,
    data: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBName) \
        .filter(DBName.id == id) \
        .update(data)
    session.commit()
    return rows

@session_wrapper
def delete(
    id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBName) \
        .filter(DBName.id == id) \
        .delete()
    session.commit()
    return rows
