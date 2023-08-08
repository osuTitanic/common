
from app.common.database.objects import DBLog

import app

def create(
    message: str,
    level: str,
    type: str
) -> DBLog:
    with app.session.database.managed_session() as session:
        session.add(
            log := DBLog(
                message,
                level,
                type
            )
        )
        session.commit()

    return log

# TODO: Create fetch queries
