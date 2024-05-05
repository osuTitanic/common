


from __future__ import annotations

from app.common.database.objects import DBResourceMirror
from app.common.helpers.caching import ttl_cache
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
@ttl_cache(ttl=60)
def fetch_all(session: Session = ...) -> List[DBResourceMirror]:
    return session.query(DBResourceMirror) \
        .order_by(DBResourceMirror.priority.asc()) \
        .all()

@session_wrapper
@ttl_cache(ttl=60)
def fetch_all_by_server(server: int, session: Session = ...) -> List[DBResourceMirror]:
    return session.query(DBResourceMirror) \
        .filter(DBResourceMirror.server == server) \
        .order_by(DBResourceMirror.priority.asc()) \
        .all()

@session_wrapper
@ttl_cache(ttl=60)
def fetch_by_type(type: int, server: int, session: Session = ...) -> List[DBResourceMirror]:
    return session.query(DBResourceMirror) \
        .filter(DBResourceMirror.type == type) \
        .filter(DBResourceMirror.server == server) \
        .order_by(DBResourceMirror.priority.asc()) \
        .all()

@session_wrapper
@ttl_cache(ttl=60)
def fetch_by_type_all(type: int, session: Session = ...) -> List[DBResourceMirror]:
    return session.query(DBResourceMirror) \
        .filter(DBResourceMirror.type == type) \
        .order_by(DBResourceMirror.priority.asc()) \
        .group_by(DBResourceMirror.url, DBResourceMirror.server) \
        .all()
