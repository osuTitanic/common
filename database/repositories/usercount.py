
from app.common.database.objects import DBUserCount

from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime

import app

def create(count: int) -> DBUserCount:
    with app.session.database.managed_session() as session:
        session.add(uc := DBUserCount(count))
        session.commit()

    return uc

def fetch_range(_until: datetime, _from: datetime) -> List[DBUserCount]:
    return app.session.database.session.query(DBUserCount) \
                .filter(and_(
                    DBUserCount.time <= _from,
                    DBUserCount.time >= _until
                )) \
                .order_by(desc(DBUserCount.time)) \
                .all()

def fetch_last() -> Optional[DBUserCount]:
    return app.session.database.session.query(DBUserCount) \
                .order_by(desc(DBUserCount.time)) \
                .first()
