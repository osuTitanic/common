
from .text import formatters as text_formatters
from .web import formatters as web_formatters

from app.common.database.repositories import activities, wrapper
from app.common.constants import UserActivity
from sqlalchemy.orm import Session
from app.common import officer

import config
import app

__all__ = [
    'submit',
    'web_formatters',
    'text_formatters'
]

def on_submit_fail(e: Exception) -> None:
    officer.call(
        f'Failed to submit highlight: "{e}"',
        exc_info=e
    )

@wrapper.exception_wrapper(on_submit_fail)
def submit(
    user_id: int,
    mode: int | None,
    type: UserActivity,
    data: dict,
    session: Session,
    is_announcement: bool = False,
    is_hidden: bool = False
) -> None:
    app.session.events.submit(
        'bancho_event',
        user_id=user_id,
        mode=mode,
        type=type.value,
        data=data,
        is_announcement=is_announcement
    )

    if is_hidden:
        return

    activities.create(
        user_id, mode,
        type, data,
        session=session
    )
