
from app.common.database.objects import DBScreenshot
from typing import Optional

import app

def create(user_id: int, hidden: bool) -> DBScreenshot:
    with app.session.database.managed_session() as session:
        session.add(
            ss := DBScreenshot(
                user_id,
                hidden
            )
        )
        session.commit()
        session.refresh(ss)

    return ss

def fetch_by_id(id: int) -> Optional[DBScreenshot]:
    return app.session.database.session.query(DBScreenshot) \
            .filter(DBScreenshot.id == id) \
            .first()
