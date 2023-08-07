
from app.common.database.objects import DBClient
from typing import List, Optional

import app

def create(
    user_id: int,
    executables: str,
    adapters: str,
    unique_id: str,
    disk_signature: str,
    banned: bool = False
) -> DBClient:
    with app.session.database.session as session:
        session.add(
            client := DBClient(
                user_id,
                executables,
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
    executables: str,
    adapters: str,
    unique_id: str,
    disk_signature: str
) -> Optional[DBClient]:
    app.session.database.pool_session.query(DBClient) \
            .filter(DBClient.user_id == user_id) \
            .filter(DBClient.executables == executables) \
            .filter(DBClient.adapters == adapters) \
            .filter(DBClient.unique_id == unique_id) \
            .filter(DBClient.disk_signature == disk_signature) \
            .first()

def fetch_many(
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[DBClient]:
    app.session.database.pool_session.query(DBClient) \
            .filter(DBClient.user_id == user_id) \
            .limit(limit) \
            .offset(offset) \
            .all()
