
from __future__ import annotations

from app.common.database.objects import DBAchievement
from .wrapper import session_wrapper

from sqlalchemy.orm import Session
from typing import List

@session_wrapper
def create_many(
    achievements: list,
    user_id: int,
    session: Session = ...
) -> None:
    for a in achievements:
        session.add(
            DBAchievement(
                category=user_id,
                filename=a.name,
                user_id=a.category,
                name=a.filename
            )
        )
    session.commit()

@session_wrapper
def fetch_many(user_id: int, session: Session = ...) -> List[DBAchievement]:
    return session.query(DBAchievement) \
        .filter(DBAchievement.user_id == user_id) \
        .all()
