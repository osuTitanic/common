
from app.common.database.objects import DBRelationship, DBUser
from sqlalchemy.orm import Session
from typing import Iterable, List

from .wrapper import session_wrapper, SessionProvider

@session_wrapper
def create(
    user_id: int,
    target_id: int,
    status: int = 0,
    session: Session = SessionProvider
) -> DBRelationship:
    session.add(
        rel := DBRelationship(
            user_id=user_id,
            target_id=target_id,
            status=status
        )
    )
    session.flush()
    session.refresh(rel)
    return rel

@session_wrapper
def delete(
    user_id: int,
    target_id: int,
    status: int = 0,
    session: Session = SessionProvider
) -> bool:
    rel = session.query(DBRelationship) \
            .filter(DBRelationship.user_id == user_id) \
            .filter(DBRelationship.target_id == target_id) \
            .filter(DBRelationship.status == status)

    if rel.first():
        rel.delete()
        session.flush()
        return True

    return False

@session_wrapper
def fetch_many_by_id(user_id: int, session: Session = SessionProvider) -> List[DBRelationship]:
    return session.query(DBRelationship) \
        .filter(DBRelationship.user_id == user_id) \
        .all()

@session_wrapper
def fetch_many_by_target(target_id: int, session: Session = SessionProvider) -> List[DBRelationship]:
    return session.query(DBRelationship) \
        .filter(DBRelationship.target_id == target_id) \
        .all()

@session_wrapper
def fetch_many_friends_by_target(
    target_id: int,
    session: Session = SessionProvider
) -> List[DBRelationship]:
    return session.query(DBRelationship) \
        .filter(DBRelationship.target_id == target_id) \
        .filter(DBRelationship.status == 0) \
        .all()

@session_wrapper
def fetch_many_blocked_by_target(
    target_id: int,
    session: Session = SessionProvider
) -> List[DBRelationship]:
    return session.query(DBRelationship) \
        .filter(DBRelationship.target_id == target_id) \
        .filter(DBRelationship.status == 1) \
        .all()

@session_wrapper
def fetch_count_by_id(user_id: int, session: Session = SessionProvider) -> int:
    return session.query(DBRelationship) \
        .filter(DBRelationship.user_id == user_id) \
        .count()

@session_wrapper
def fetch_count_by_target(target_id: int, session: Session = SessionProvider) -> int:
    return session.query(DBRelationship) \
        .filter(DBRelationship.target_id == target_id) \
        .count()

@session_wrapper
def fetch_target_ids(user_id: int, session: Session = SessionProvider) -> List[int]:
    result = session.query(DBRelationship.target_id) \
        .filter(DBRelationship.user_id == user_id) \
        .all()

    return [id[0] for id in result]

@session_wrapper
def fetch_target_ids_in(
    user_id: int,
    target_ids: Iterable[int],
    session: Session = SessionProvider
) -> List[int]:
    target_ids = tuple(target_ids)

    if not target_ids:
        return []

    result = session.query(DBRelationship.target_id) \
        .filter(DBRelationship.user_id == user_id) \
        .filter(DBRelationship.target_id.in_(target_ids)) \
        .all()

    return [id[0] for id in result]

@session_wrapper
def is_friend(
    user_id: int,
    target_id: int,
    session: Session = SessionProvider
) -> bool:
    return session.query(DBRelationship.target_id) \
        .filter(DBRelationship.user_id == user_id) \
        .filter(DBRelationship.target_id == target_id) \
        .filter(DBRelationship.status == 0) \
        .first() is not None

@session_wrapper
def is_blocked(
    user_id: int,
    target_id: int,
    session: Session = SessionProvider
) -> bool:
    return session.query(DBRelationship.target_id) \
        .filter(DBRelationship.user_id == user_id) \
        .filter(DBRelationship.target_id == target_id) \
        .filter(DBRelationship.status == 1) \
        .first() is not None

@session_wrapper
def fetch_users(
    user_id: int,
    status: int = 0,
    session: Session = SessionProvider
) -> List[DBUser]:
    return session.query(DBUser) \
            .join(DBRelationship, DBUser.id == DBRelationship.target_id) \
            .filter(DBRelationship.user_id == user_id) \
            .filter(DBRelationship.status == status) \
            .order_by(DBRelationship.user_id.asc()) \
            .all()
