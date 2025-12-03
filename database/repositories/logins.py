
from __future__ import annotations

from app.common.database.objects import DBLogin
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    ip: str,
    version: str,
    session: Session = ...
) -> DBLogin:
    session.add(
        login := DBLogin(
            user_id=user_id,
            ip=ip,
            version=version,
            time=datetime.now()
        )
    )
    session.commit()
    return login

@session_wrapper
def fetch_many(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    session: Session = ...
) -> List[DBLogin]:
    return session.query(DBLogin) \
        .filter(DBLogin.user_id == user_id) \
        .order_by(DBLogin.time.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_many_until(
    user_id: int,
    until: datetime,
    session: Session = ...
) -> List[DBLogin]:
    return session.query(DBLogin) \
        .filter(DBLogin.user_id == user_id) \
        .filter(DBLogin.time > until) \
        .order_by(DBLogin.time.desc()) \
        .all()

@session_wrapper
def fetch_many_by_ip(
    ip: str,
    limit: int = 50,
    offset: int = 0,
    session: Session = ...
) -> List[DBLogin]:
    return session.query(DBLogin) \
        .filter(DBLogin.ip == ip) \
        .order_by(DBLogin.time.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_many_by_version(
    version: str,
    limit: int = 50,
    offset: int = 0,
    session: Session = ...
) -> List[DBLogin]:
    return session.query(DBLogin) \
        .filter(DBLogin.version == version) \
        .order_by(DBLogin.time.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_last_osu_version(
    user_id: int,
    session: Session = ...
) -> str | None:
    login = session.query(DBLogin.version) \
        .filter(DBLogin.user_id == user_id) \
        .filter(DBLogin.version.like('b%')) \
        .order_by(DBLogin.time.desc()) \
        .first()
    return login[0] if login else None
