
from __future__ import annotations
from typing import List, Dict, Tuple

from app.common.database.objects import DBRating
from sqlalchemy.orm import Session
from sqlalchemy import func

from .wrapper import session_wrapper

@session_wrapper
def create(
    beatmap_hash: str,
    user_id: int,
    set_id: int,
    rating: int,
    session: Session = ...
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
def fetch_one(beatmap_hash: str, user_id: int, session: Session = ...) -> int | None:
    result = session.query(DBRating.rating) \
        .filter(DBRating.map_checksum == beatmap_hash) \
        .filter(DBRating.user_id == user_id) \
        .first()

    return result[0] if result else None

@session_wrapper
def fetch_many(beatmap_hash: str, session: Session = ...) -> List[int]:
    return [
        rating[0]
        for rating in session.query(DBRating.rating) \
            .filter(DBRating.map_checksum == beatmap_hash) \
            .all()
    ]

@session_wrapper
def fetch_average(beatmap_hash: str, session: Session = ...) -> float:
    result = session.query(
        func.avg(DBRating.rating).label('average')) \
        .filter(DBRating.map_checksum == beatmap_hash) \
        .first()[0]

    return float(result) if result else 0.0

@session_wrapper
def fetch_average_by_set(set_id: int, session: Session = ...) -> float:
    result = session.query(
        func.avg(DBRating.rating).label('average')) \
        .filter(DBRating.set_id == set_id) \
        .first()[0]

    return float(result) if result else 0.0

@session_wrapper
def fetch_range(beatmap_hash: str, session: Session = ...) -> Dict[int, int]:
    result = session.query(DBRating.rating, func.count()) \
        .filter(DBRating.map_checksum == beatmap_hash) \
        .group_by(DBRating.rating) \
        .all()

    return {
        rating: count
        for rating, count in result
    }

@session_wrapper
def fetch_range_by_set(set_id: int, session: Session = ...) -> Dict[int, int]:
    result = session.query(DBRating.rating, func.count()) \
        .filter(DBRating.set_id == set_id) \
        .group_by(DBRating.rating) \
        .all()

    return {
        rating: count
        for rating, count in result
    }

@session_wrapper
def fetch_ratio(beatmap_hash: str, session: Session = ...) -> Tuple[int, int]:
    result = session.query(
        func.count(DBRating.rating).filter(DBRating.rating >= 5).label('count_good'),
        func.count(DBRating.rating).filter(DBRating.rating < 5).label('count_bad')
    ) \
        .filter(DBRating.map_checksum == beatmap_hash) \
        .first()

    if result is None:
        return 0, 0

    return result[0] or 0, result[1] or 0

@session_wrapper
def fetch_ratio_by_set(set_id: int, session: Session = ...) -> Tuple[int, int]:
    result = session.query(
        func.count(DBRating.rating).filter(DBRating.rating >= 5).label('count_good'),
        func.count(DBRating.rating).filter(DBRating.rating < 5).label('count_bad')
    ) \
        .filter(DBRating.set_id == set_id) \
        .first()

    if result is None:
        return 0, 0

    return result[0] or 0, result[1] or 0

@session_wrapper
def delete(beatmap_hash: str, user_id: int, session: Session = ...) -> None:
    session.query(DBRating) \
        .filter(DBRating.map_checksum == beatmap_hash) \
        .filter(DBRating.user_id == user_id) \
        .delete()
    session.commit()

@session_wrapper
def delete_by_set_id(set_id: int, session: Session = ...) -> None:
    session.query(DBRating) \
        .filter(DBRating.set_id == set_id) \
        .delete()
    session.commit()
