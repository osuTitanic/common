
from __future__ import annotations

from app.common.database.objects import DBReport
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    target_id: int,
    sender_id: int,
    reason: str | None = None,
    session: Session = ...
) -> DBReport:
    session.add(
        r := DBReport(
            target_id=target_id,
            sender_id=sender_id,
            reason=reason,
            time=datetime.now()
        )
    )
    session.flush()
    session.refresh(r)
    return r

@session_wrapper
def fetch_by_id(id: int, session: Session = ...) -> DBReport | None:
    return session.query(DBReport) \
        .filter(DBReport.id == id) \
        .first()

@session_wrapper
def fetch_last_by_sender(sender_id: int, session: Session = ...) -> DBReport | None:
    return session.query(DBReport) \
        .filter(DBReport.sender_id == sender_id) \
        .filter(DBReport.resolved == False) \
        .order_by(DBReport.time.desc()) \
        .first()

@session_wrapper
def fetch_last(target_id: int, session: Session = ...) -> DBReport | None:
    return session.query(DBReport) \
        .filter(DBReport.target_id == target_id) \
        .filter(DBReport.resolved == False) \
        .order_by(DBReport.time.desc()) \
        .first()

@session_wrapper
def fetch_all_by_sender(sender_id: int, session: Session = ...) -> List[DBReport]:
    return session.query(DBReport) \
        .filter(DBReport.sender_id == sender_id) \
        .filter(DBReport.resolved == False) \
        .order_by(DBReport.time.desc()) \
        .all()

@session_wrapper
def fetch_all(target_id: int, session: Session = ...) -> List[DBReport]:
    return session.query(DBReport) \
        .filter(DBReport.target_id == target_id) \
        .filter(DBReport.resolved == False) \
        .order_by(DBReport.time.desc()) \
        .all()

@session_wrapper
def fetch_by_sender_to_target(
    sender_id: int,
    target_id: int,
    session: Session = ...
) -> DBReport | None:
    return session.query(DBReport) \
        .filter(DBReport.target_id == target_id) \
        .filter(DBReport.sender_id == sender_id) \
        .filter(DBReport.resolved == False) \
        .order_by(DBReport.time.desc()) \
        .first()

@session_wrapper
def update(
    id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBReport) \
        .filter(DBReport.id == id) \
        .update(updates)
    session.flush()
    return rows
