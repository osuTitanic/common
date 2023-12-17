
from app.common.database.objects import DBInfringement
from datetime import datetime, timedelta
from typing import Optional, List

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
    with app.session.database.managed_session() as session:
        return session.query(DBInfringement) \
            .filter(DBInfringement.user_id == user_id) \
            .order_by(DBInfringement.id.desc()) \
            .first()

def fetch_recent_by_action(user_id: int, action: int) -> Optional[DBInfringement]:
    with app.session.database.managed_session() as session:
        return session.query(DBInfringement) \
            .filter(DBInfringement.user_id == user_id) \
            .filter(DBInfringement.action == action) \
            .order_by(DBInfringement.id.desc()) \
            .first()

def fetch_all(user_id: int) -> List[DBInfringement]:
    with app.session.database.managed_session() as session:
        return session.query(DBInfringement) \
            .filter(DBInfringement.user_id == user_id) \
            .order_by(DBInfringement.id.desc()) \
            .all()

def fetch_all_by_action(user_id: int, action: int) -> List[DBInfringement]:
    with app.session.database.managed_session() as session:
        return session.query(DBInfringement) \
            .filter(DBInfringement.user_id == user_id) \
            .filter(DBInfringement.action == action) \
            .order_by(DBInfringement.time.desc()) \
            .all()

def delete_by_id(id: int) -> None:
    with app.session.database.managed_session() as session:
        session.query(DBInfringement) \
            .filter(DBInfringement.id == id) \
            .delete()

def delete_old(user_id: int, delete_after=timedelta(weeks=5), remove_permanent=False) -> int:
    if not remove_permanent:
        return app.session.database.session.query(DBInfringement) \
                        .filter(DBInfringement.user_id == user_id) \
                        .filter(DBInfringement.time < datetime.now() - delete_after) \
                        .filter(DBInfringement.is_permanent == False) \
                        .delete()

    return app.session.database.session.query(DBInfringement) \
                    .filter(DBInfringement.user_id == user_id) \
                    .filter(DBInfringement.time < datetime.now() - delete_after) \
                    .delete()
