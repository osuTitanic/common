
from __future__ import annotations

from app.common.database.objects import DBClient
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
    # TODO: There are somehow two types of empty md5 hashes?
    return session.query(DBClient) \
        .filter(or_(
            and_(
                DBClient.adapters == adapters,
                DBClient.adapters != "b4ec3c4334a0249dae95c284ec5983df", # "runningunderwine"
                DBClient.adapters != "74be16979710d4c4e7c6647856088456", # ""
                DBClient.adapters != "d41d8cd98f00b204e9800998ecf8427e"  # ""
            ),
            and_(
                DBClient.disk_signature == disk_signature,
                DBClient.disk_signature != "ad921d60486366258809553a3db49a4a", # "unknown"
                DBClient.disk_signature != "dcfcd07e645d245babe887e5e2daa016", # "0"
                DBClient.disk_signature != "28c8edde3d61a0411511d3b1866f0636", # "1"
                DBClient.disk_signature != "74be16979710d4c4e7c6647856088456", # ""
                DBClient.disk_signature != "d41d8cd98f00b204e9800998ecf8427e"  # ""
            ),
            and_(
                DBClient.unique_id == unique_id,
                DBClient.unique_id != "ad921d60486366258809553a3db49a4a", # "unknown"
                DBClient.unique_id != "74be16979710d4c4e7c6647856088456", # ""
                DBClient.unique_id != "d41d8cd98f00b204e9800998ecf8427e"  # ""
            )
        )).all()

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
        .offset(offset) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_all(user_id: int, session: Session | None = None) -> List[DBClient]:
    """Fetch every client from user id"""
    return session.query(DBClient) \
        .filter(DBClient.user_id == user_id) \
        .all()
