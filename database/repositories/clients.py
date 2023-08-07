
from app.common.database.objects import DBClient
from typing import List, Optional

import app

def create(
    user_id: int,
    executable: str,
    adapters: str,
    unique_id: str,
    disk_signature: str,
    banned: bool = False
) -> DBClient:
    with app.session.database.session as session:
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

def fetch_one(
    user_id: int,
    executable: str,
    adapters: str,
    unique_id: str,
    disk_signature: str
) -> Optional[DBClient]:
    """Fetch one client where all hardware attributes need to match"""
    return app.session.database.pool_session.query(DBClient) \
            .filter(DBClient.user_id == user_id) \
            .filter(DBClient.executable == executable) \
            .filter(DBClient.adapters == adapters) \
            .filter(DBClient.unique_id == unique_id) \
            .filter(DBClient.disk_signature == disk_signature) \
            .first()

def fetch_without_executable(
    user_id: int,
    adapters: str,
    unique_id: str,
    disk_signature: str
) -> Optional[DBClient]:
    """Fetch one client with matching hardware and user id"""
    return app.session.database.pool_session.query(DBClient) \
            .filter(DBClient.user_id == user_id) \
            .filter(DBClient.adapters == adapters) \
            .filter(DBClient.unique_id == unique_id) \
            .filter(DBClient.disk_signature == disk_signature) \
            .first()

def fetch_hardware_only(
    adapters: str,
    unique_id: str,
    disk_signature: str
) -> List[DBClient]:
    """Fetch clients only by hardware attributes. Useful for multi-account detection."""
    return app.session.database.pool_session.query(DBClient) \
            .filter(DBClient.adapters == adapters) \
            .filter(DBClient.unique_id == unique_id) \
            .filter(DBClient.disk_signature == disk_signature) \
            .all()

def fetch_many(
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[DBClient]:
    """Fetch every client from user id"""
    return app.session.database.pool_session.query(DBClient) \
            .filter(DBClient.user_id == user_id) \
            .limit(limit) \
            .offset(offset) \
            .all()
