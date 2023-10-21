
from app.common.database.objects import DBActivity
from datetime import datetime, timedelta

import app

def create(
    user_id: int,
    mode: int,
    text: str,
    args: str,
    links: str
) -> DBActivity:
    with app.session.database.managed_session() as session:
        session.add(
            ac := DBActivity(
                user_id,
                mode,
                text,
                args,
                links
            )
        )
        session.commit()
        session.refresh(ac)

    return ac

def fetch_recent(user_id: int, mode: int, until: timedelta = timedelta(days=30)):
    return app.session.database.session.query(DBActivity) \
                .filter(DBActivity.time > datetime.now() - until) \
                .filter(DBActivity.user_id == user_id) \
                .filter(DBActivity.mode == mode) \
                .order_by(DBActivity.id.desc()) \
                .all()
