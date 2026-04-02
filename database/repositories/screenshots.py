
from app.common.database.objects import DBScreenshot
from sqlalchemy.orm import Session

from .wrapper import session_wrapper, SessionProvider

@session_wrapper
def create(
    user_id: int,
    hidden: bool,
    session: Session = SessionProvider
) -> DBScreenshot:
    session.add(
        ss := DBScreenshot(
            user_id=user_id,
            hidden=hidden
        )
    )
    session.flush()
    session.refresh(ss)
    return ss

@session_wrapper
def fetch_by_id(
    id: int,
    session: Session = SessionProvider
) -> DBScreenshot | None:
    return session.query(DBScreenshot) \
        .filter(DBScreenshot.id == id) \
        .first()
