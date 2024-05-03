


from __future__ import annotations

from app.common.database.objects import DBRelease
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def fetch_by_name(name: str, session: Session = ...) -> DBRelease | None:
    return session.query(DBRelease) \
        .filter(DBRelease.name == name) \
        .first()

@session_wrapper
def fetch_all(session: Session = ...) -> List[DBRelease]:
    return session.query(DBRelease) \
        .order_by(DBRelease.version.desc()) \
        .all()
