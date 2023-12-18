
from __future__ import annotations

from app.common.database.objects import DBAchievement
from app.common.objects import bAchievement
from .wrapper import session_wrapper

from sqlalchemy.orm import Session
from typing import List

@session_wrapper
def create_many(
    achievements: List[bAchievement],
    user_id: int,
    session: Session | None = None
) -> None:
    for a in achievements:
        session.add(
            DBAchievement(
                user_id,
                a.name,
                a.category,
                a.filename
            )
        )
    session.commit()

@session_wrapper
def fetch_many(user_id: int, session: Session | None = None) -> List[DBAchievement]:
    return session.query(DBAchievement) \
        .filter(DBAchievement.user_id == user_id) \
        .all()
