
from __future__ import annotations

from app.common.database.objects import DBName
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(user_id: int, old_name: str, session: Session = ...) -> DBName:
    session.add(name := DBName(user_id, old_name))
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
def fetch_by_name_reserved(name: str, session: Session = ...) -> DBName | None:
    return session.query(DBName) \
        .filter(or_(
            DBName.name.ilike(name),
            DBName.name.ilike(f'%{name}%')
        )) \
        .filter(DBName.reserved == True) \
        .order_by(func.length(DBName.name).asc()) \
        .first()
