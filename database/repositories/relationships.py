
from __future__ import annotations

from app.common.database.objects import DBRelationship
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    target_id: int,
    status: int = 0,
    session: Session | None = None
) -> DBRelationship:
    session.add(
        rel := DBRelationship(
            user_id,
            target_id,
            status
        )
    )
    session.commit()
    session.refresh(rel)
    return rel

@session_wrapper
def delete(
    user_id: int,
    target_id: int,
    status: int = 0,
    session: Session | None = None
) -> bool:
    rel = session.query(DBRelationship) \
            .filter(DBRelationship.user_id == user_id) \
            .filter(DBRelationship.target_id == target_id) \
            .filter(DBRelationship.status == status)

    if rel.first():
        rel.delete()
        session.commit()
        return True

    return False

@session_wrapper
def fetch_many_by_id(user_id: int, session: Session | None = None) -> List[DBRelationship]:
    return session.query(DBRelationship) \
        .filter(DBRelationship.user_id == user_id) \
        .all()

@session_wrapper
def fetch_many_by_target(target_id: int, session: Session | None = None) -> List[DBRelationship]:
        return session.query(DBRelationship) \
            .filter(DBRelationship.target_id == target_id) \
            .all()

@session_wrapper
def fetch_count_by_id(user_id: int, session: Session | None = None) -> int:
    return session.query(DBRelationship) \
        .filter(DBRelationship.user_id == user_id) \
        .count()

@session_wrapper
def fetch_count_by_target(target_id: int, session: Session | None = None) -> int:
    return session.query(DBRelationship) \
        .filter(DBRelationship.target_id == target_id) \
        .count()

@session_wrapper
def fetch_target_ids(user_id: int, session: Session | None = None) -> List[int]:
    result = session.query(DBRelationship.target_id) \
        .filter(DBRelationship.user_id == user_id) \
        .all()

    return [id[0] for id in result]
