
from app.common.database.objects import DBInfringement
from typing import Optional, List
from datetime import datetime

import app

def create(
    user_id: int,
    action: int,
    length: datetime,
    description: Optional[str] = None,
    is_permanent: bool = False
) -> DBInfringement:
    with app.session.database.managed_session() as session:
        session.add(
            i := DBInfringement(
                user_id,
                action,
                length,
                description,
                is_permanent
            )
        )
        session.commit()
        session.refresh(i)

    return i

def fetch_recent(user_id: int) -> Optional[DBInfringement]:
    return app.session.database.session.query(DBInfringement) \
                    .filter(DBInfringement.user_id == user_id) \
                    .order_by(DBInfringement.id.desc()) \
                    .first()

def fetch_recent_by_action(user_id: int, action: int) -> List[DBInfringement]:
    return app.session.database.session.query(DBInfringement) \
                    .filter(DBInfringement.user_id == user_id) \
                    .filter(DBInfringement.action == action) \
                    .order_by(DBInfringement.id.desc()) \
                    .first()

def fetch_all(user_id: int) -> List[DBInfringement]:
    return app.session.database.session.query(DBInfringement) \
                    .filter(DBInfringement.user_id == user_id) \
                    .order_by(DBInfringement.id.desc()) \
                    .all()

def fetch_all_by_action(user_id: int, action: int) -> List[DBInfringement]:
    return app.session.database.session.query(DBInfringement) \
                    .filter(DBInfringement.user_id == user_id) \
                    .filter(DBInfringement.action == action) \
                    .order_by(DBInfringement.time.desc()) \
                    .all()
