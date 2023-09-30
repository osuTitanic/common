
from app.common.database import DBReport
from typing import Optional, List

import app

def create(
    target_id: int,
    sender_id: int,
    reason: Optional[str] = None
) -> DBReport:
    with app.session.database.managed_session() as session:
        session.add(
            r := DBReport(
                target_id,
                sender_id,
                reason
            )
        )
        session.commit()
        session.refresh(r)

    return r

def fetch_by_id(id: int) -> Optional[DBReport]:
    return app.session.database.session.query(DBReport) \
                .filter(DBReport.id == id) \
                .first()

def fetch_last_by_sender(sender_id: int) -> Optional[DBReport]:
    return app.session.database.session.query(DBReport) \
                .filter(DBReport.sender_id == sender_id) \
                .filter(DBReport.resolved == False) \
                .order_by(DBReport.time.desc()) \
                .first()

def fetch_last(target_id: int) -> Optional[DBReport]:
    return app.session.database.session.query(DBReport) \
                .filter(DBReport.target_id == target_id) \
                .filter(DBReport.resolved == False) \
                .order_by(DBReport.time.desc()) \
                .first()

def fetch_all_by_sender(sender_id: int) -> List[DBReport]:
    return app.session.database.session.query(DBReport) \
                .filter(DBReport.sender_id == sender_id) \
                .filter(DBReport.resolved == False) \
                .order_by(DBReport.time.desc()) \
                .all()

def fetch_all(target_id: int) -> List[DBReport]:
    return app.session.database.session.query(DBReport) \
                .filter(DBReport.target_id == target_id) \
                .filter(DBReport.resolved == False) \
                .order_by(DBReport.time.desc()) \
                .all()

def fetch_by_sender_to_target(
    sender_id: int,
    target_id: int
) -> Optional[DBReport]:
    return app.session.database.session.query(DBReport) \
                .filter(DBReport.target_id == target_id) \
                .filter(DBReport.sender_id == sender_id) \
                .filter(DBReport.resolved == False) \
                .order_by(DBReport.time.desc()) \
                .first()
