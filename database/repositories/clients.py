
from __future__ import annotations

from app.common.database.objects import DBClient
from sqlalchemy.orm import Session

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    executable: str,
    adapters: str,
    unique_id: str,
    disk_signature: str,
    banned: bool = False,
    session: Session | None = None
) -> DBClient:
    session.add(
        client := DBClient(
            user_id,
            executable,
            adapters,
            unique_id,
            disk_signature,
            banned
        )
    )
    session.commit()
    return client

@session_wrapper
def update_all(
    user_id: int,
    updates: dict,
    session: Session | None = None
) -> int:
    rows = session.query(DBClient) \
        .filter(DBClient.user_id == user_id) \
        .update(updates)
    session.commit()
    return rows

@session_wrapper
def fetch_one(
    user_id: int,
    executable: str,
    adapters: str,
    unique_id: str,
    disk_signature: str,
    session: Session | None = None
) -> DBClient | None:
    """Fetch one client where all hardware attributes need to match"""
    return session.query(DBClient) \
        .filter(DBClient.user_id == user_id) \
        .filter(DBClient.executable == executable) \
        .filter(DBClient.adapters == adapters) \
        .filter(DBClient.unique_id == unique_id) \
        .filter(DBClient.disk_signature == disk_signature) \
        .first()

@session_wrapper
def fetch_without_executable(
    user_id: int,
    adapters: str,
    unique_id: str,
    disk_signature: str,
    session: Session | None = None
) -> DBClient | None:
    """Fetch one client with matching hardware and user id"""
    return session.query(DBClient) \
        .filter(DBClient.user_id == user_id) \
        .filter(DBClient.adapters == adapters) \
        .filter(DBClient.unique_id == unique_id) \
        .filter(DBClient.disk_signature == disk_signature) \
        .first()

@session_wrapper
def fetch_hardware_only(
    adapters: str,
    unique_id: str,
    disk_signature: str,
    session: Session | None = None
) -> List[DBClient]:
    """Fetch clients only by hardware attributes. Useful for multi-account detection."""
    return session.query(DBClient) \
        .filter(DBClient.adapters == adapters) \
        .filter(DBClient.unique_id == unique_id) \
        .filter(DBClient.disk_signature == disk_signature) \
        .all()

@session_wrapper
def fetch_many(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    session: Session | None = None
) -> List[DBClient]:
    """Fetch every client from user id"""
    return session.query(DBClient) \
        .filter(DBClient.user_id == user_id) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_all(user_id: int, session: Session | None = None) -> List[DBClient]:
    """Fetch every client from user id"""
    return session.query(DBClient) \
        .filter(DBClient.user_id == user_id) \
        .all()
