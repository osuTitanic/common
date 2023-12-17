
from app.common.database.objects import DBRating

from typing import List, Optional
from sqlalchemy import func

import app

def create(
    beatmap_hash: str,
    user_id: int,
    set_id: int,
    rating: int
) -> DBRating:
    with app.session.database.managed_session() as session:
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

def fetch_one(beatmap_hash: str, user_id: int) -> Optional[int]:
    with app.session.database.managed_session() as session:
        result = session.query(DBRating.rating) \
            .filter(DBRating.map_checksum == beatmap_hash) \
            .filter(DBRating.user_id == user_id) \
            .first()

    return result[0] if result else None

def fetch_many(beatmap_hash: str) -> List[int]:
    with app.session.database.managed_session() as session:
        return [
            rating[0]
            for rating in session.query(DBRating.rating) \
                .filter(DBRating.map_checksum == beatmap_hash) \
                .all()
        ]

def fetch_average(beatmap_hash: str) -> float:
    with app.session.database.managed_session() as session:
        result = session.query(
            func.avg(DBRating.rating).label('average')) \
            .filter(DBRating.map_checksum == beatmap_hash) \
            .first()[0]

    return float(result) if result else 0.0
