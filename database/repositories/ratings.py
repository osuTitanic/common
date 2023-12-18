
from __future__ import annotations

from app.common.database.objects import DBRating

from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from .wrapper import session_wrapper

@session_wrapper
def create(
    beatmap_hash: str,
    user_id: int,
    set_id: int,
    rating: int,
    session: Session | None = None
) -> DBRating:
    session.add(
        rating := DBRating(
            user_id,
            set_id,
            beatmap_hash,
            rating
        )
    )
    session.commit()
    session.refresh(rating)
    return rating

@session_wrapper
def fetch_one(beatmap_hash: str, user_id: int, session: Session | None = None) -> Optional[int]:
    result = session.query(DBRating.rating) \
        .filter(DBRating.map_checksum == beatmap_hash) \
        .filter(DBRating.user_id == user_id) \
        .first()

    return result[0] if result else None

@session_wrapper
def fetch_many(beatmap_hash: str, session: Session | None = None) -> List[int]:
    return [
        rating[0]
        for rating in session.query(DBRating.rating) \
            .filter(DBRating.map_checksum == beatmap_hash) \
            .all()
    ]

@session_wrapper
def fetch_average(beatmap_hash: str, session: Session | None = None) -> float:
    result = session.query(
        func.avg(DBRating.rating).label('average')) \
        .filter(DBRating.map_checksum == beatmap_hash) \
        .first()[0]

    return float(result) if result else 0.0
