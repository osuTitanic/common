
from __future__ import annotations

from app.common.database.objects import DBClient, DBVerifiedClient
from app.common.helpers.caching import ttl_cache

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    executable: str,
    adapters: str,
    unique_id: str,
    disk_signature: str,
    banned: bool = False,
    session: Session = ...
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
    session: Session = ...
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
    session: Session = ...
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
    session: Session = ...
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
    session: Session = ...
) -> List[DBClient]:
    """Fetch clients only by hardware attributes. Used for multi-account detection."""
    return session.query(DBClient) \
        .filter(or_(
            and_(
                DBClient.adapters == adapters,
                *[
                    DBClient.adapters != hash
                    for hash in fetch_verified(0)
                ]
            ),
            and_(
                DBClient.unique_id == unique_id,
                *[
                    DBClient.unique_id != hash
                    for hash in fetch_verified(1)
                ]
            ),
            and_(
                DBClient.disk_signature == disk_signature,
                *[
                    DBClient.disk_signature != hash
                    for hash in fetch_verified(2)
                ]
            )
        )).all()

@session_wrapper
def fetch_many(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    session: Session = ...
) -> List[DBClient]:
    """Fetch every client from user id"""
    return session.query(DBClient) \
        .filter(DBClient.user_id == user_id) \
        .offset(offset) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_all(user_id: int, session: Session = ...) -> List[DBClient]:
    """Fetch every client from user id"""
    return session.query(DBClient) \
        .filter(DBClient.user_id == user_id) \
        .all()

@session_wrapper
@ttl_cache(ttl=600)
def fetch_verified(type: int, session: Session = ...) -> List[str]:
    """Fetch all hardware ids, that can bypass multiaccounting checks"""
    return [
        hash_tuple[0] for hash_tuple in
        session.query(DBVerifiedClient.hash) \
            .filter(DBVerifiedClient.type == type) \
            .all()
    ]
