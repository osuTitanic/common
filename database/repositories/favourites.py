
from app.common.database.objects import DBFavourite
from typing import List, Optional

import app

def create(
    user_id: int,
    set_id: int
) -> Optional[DBFavourite]:
    with app.session.database.managed_session() as session:
        # Check if favourite was already set
        if session.query(DBFavourite.user_id) \
            .filter(DBFavourite.user_id == user_id) \
            .filter(DBFavourite.set_id == set_id) \
            .first():
            return None

        session.add(
            fav := DBFavourite(
                user_id,
                set_id
            )
        )
        session.commit()

    return fav

def fetch_one(
    user_id: int,
    set_id: int
) -> Optional[DBFavourite]:
    return app.session.database.session.query(DBFavourite) \
            .filter(DBFavourite.user_id == user_id) \
            .filter(DBFavourite.set_id == set_id) \
            .first()

def fetch_many(user_id: int) -> List[DBFavourite]:
    return app.session.database.session.query(DBFavourite) \
            .filter(DBFavourite.user_id == user_id) \
            .all()

def fetch_many_by_set(set_id: int, limit: int = 5) -> int:
    return app.session.database.session.query(DBFavourite) \
            .filter(DBFavourite.set_id == set_id) \
            .limit(limit) \
            .all()

def fetch_count(user_id: int) -> int:
    return app.session.database.session.query(DBFavourite) \
            .filter(DBFavourite.user_id == user_id) \
            .count()

def fetch_count_by_set(set_id: int) -> int:
    return app.session.database.session.query(DBFavourite) \
            .filter(DBFavourite.set_id == set_id) \
            .count()