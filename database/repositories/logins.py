
from app.common.database.objects import DBLogin
from datetime import datetime
from typing import List

import app

def create(
    user_id: int,
    ip: str,
    version: str
) -> DBLogin:
    with app.session.database.managed_session() as session:
        session.add(
            login := DBLogin(
                user_id,
                ip,
                version
            )
        )
        session.commit()

    return login

def fetch_many(
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[DBLogin]:
    return app.session.database.session.query(DBLogin) \
            .filter(DBLogin.user_id == user_id) \
            .order_by(DBLogin.time.desc()) \
            .limit(limit) \
            .offset(offset) \
            .all()

def fetch_many_until(
    user_id: int,
    until: datetime
) -> List[DBLogin]:
    return app.session.database.session.query(DBLogin) \
            .filter(DBLogin.user_id == user_id) \
            .filter(DBLogin.time > until) \
            .order_by(DBLogin.time.desc()) \
            .all()

def fetch_many_by_ip(
    ip: str,
    limit: int = 50,
    offset: int = 0
) -> List[DBLogin]:
    return app.session.database.session.query(DBLogin) \
            .filter(DBLogin.ip == ip) \
            .order_by(DBLogin.time.desc()) \
            .limit(limit) \
            .offset(offset) \
            .all()

def fetch_many_by_version(
    version: str,
    limit: int = 50,
    offset: int = 0
) -> List[DBLogin]:
    return app.session.database.session.query(DBLogin) \
            .filter(DBLogin.version == version) \
            .order_by(DBLogin.time.desc()) \
            .limit(limit) \
            .offset(offset) \
            .all()
