
from app.common.database.objects import DBChannel
from typing import List

import app

def create(
    name: str,
    topic: str,
    read_permissions: int,
    write_permissions: int
) -> DBChannel:
    with app.session.database.managed_session() as session:
        session.add(
            chan := DBChannel(
                name,
                topic,
                read_permissions,
                write_permissions
            )
        )
        session.commit()

    return chan

def fetch_all() -> List[DBChannel]:
    return app.session.database.session \
                      .query(DBChannel) \
                      .all()
