
from __future__ import annotations

from app.common.database.objects import DBName
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(user_id: int, old_name: str, session: Session | None = None) -> DBName:
    session.add(name := DBName(user_id, old_name))
    session.commit()
    return name

@session_wrapper
def fetch_one(id: int, session: Session | None = None) -> DBName:
    return session.query(DBName) \
        .filter(DBName.id == id) \
        .first()

@session_wrapper
def fetch_all(user_id: int, session: Session | None = None) -> List[DBName]:
    return session.query(DBName) \
        .filter(DBName.user_id == user_id) \
        .all()

@session_wrapper
def fetch_by_name(name: str, session: Session | None = None) -> DBName | None:
    return session.query(DBName) \
        .filter(DBName.name == name) \
        .first()

@session_wrapper
def fetch_by_name_extended(name: str, session: Session | None = None) -> DBName | None:
    return session.query(DBName) \
        .filter(DBName.name.ilike(f'%{name}%')) \
        .first()
