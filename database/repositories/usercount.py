
from app.common.database.objects import DBUserCount

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import desc, and_

import app

def create(count: int) -> DBUserCount:
    with app.session.database.managed_session() as session:
        session.add(uc := DBUserCount(count))
        session.commit()

    return uc

def fetch_range(_until: datetime, _from: datetime) -> List[DBUserCount]:
    with app.session.database.managed_session() as session:
        return session.query(DBUserCount) \
            .filter(and_(
                DBUserCount.time <= _from,
                DBUserCount.time >= _until
            )) \
            .order_by(desc(DBUserCount.time)) \
            .all()

def fetch_last() -> Optional[DBUserCount]:
    with app.session.database.managed_session() as session:
        return session.query(DBUserCount) \
            .order_by(desc(DBUserCount.time)) \
            .first()

def delete_old(delta: timedelta = timedelta(weeks=5)) -> int:
    """Delete usercount entries that are older than the given delta (default ~1 month)"""
    with app.session.database.managed_session() as session:
        rows = session.query(DBUserCount) \
                .filter(DBUserCount.time <= (datetime.now() - delta)) \
                .delete()
        session.commit()

    return rows
