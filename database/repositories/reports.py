
from __future__ import annotations

from app.common.database import DBReport
from sqlalchemy.orm import Session
from typing import Optional, List

from .wrapper import session_wrapper

@session_wrapper
def create(
    target_id: int,
    sender_id: int,
    reason: Optional[str] = None,
    session: Session | None = None
) -> DBReport:
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

@session_wrapper
def fetch_by_id(id: int, session: Session | None = None) -> Optional[DBReport]:
    return session.query(DBReport) \
        .filter(DBReport.id == id) \
        .first()

@session_wrapper
def fetch_last_by_sender(sender_id: int, session: Session | None = None) -> Optional[DBReport]:
    return session.query(DBReport) \
        .filter(DBReport.sender_id == sender_id) \
        .filter(DBReport.resolved == False) \
        .order_by(DBReport.time.desc()) \
        .first()

@session_wrapper
def fetch_last(target_id: int, session: Session | None = None) -> Optional[DBReport]:
    return session.query(DBReport) \
        .filter(DBReport.target_id == target_id) \
        .filter(DBReport.resolved == False) \
        .order_by(DBReport.time.desc()) \
        .first()

@session_wrapper
def fetch_all_by_sender(sender_id: int, session: Session | None = None) -> List[DBReport]:
    return session.query(DBReport) \
        .filter(DBReport.sender_id == sender_id) \
        .filter(DBReport.resolved == False) \
        .order_by(DBReport.time.desc()) \
        .all()

@session_wrapper
def fetch_all(target_id: int, session: Session | None = None) -> List[DBReport]:
    return session.query(DBReport) \
        .filter(DBReport.target_id == target_id) \
        .filter(DBReport.resolved == False) \
        .order_by(DBReport.time.desc()) \
        .all()

@session_wrapper
def fetch_by_sender_to_target(
    sender_id: int,
    target_id: int,
    session: Session | None = None
) -> Optional[DBReport]:
    return session.query(DBReport) \
        .filter(DBReport.target_id == target_id) \
        .filter(DBReport.sender_id == sender_id) \
        .filter(DBReport.resolved == False) \
        .order_by(DBReport.time.desc()) \
        .first()
