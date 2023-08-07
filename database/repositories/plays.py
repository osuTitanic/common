
from app.common.database.objects import DBPlay

from sqlalchemy import func

import app

def create(
    beatmap_file: str,
    beatmap_id: int,
    user_id: int,
    set_id: int,
    count: int = 1
) -> DBPlay:
    with app.session.database.session as session:
        session.add(
            p := DBPlay(
                user_id,
                beatmap_id,
                set_id,
                beatmap_file,
                count
            )
        )
        session.commit()

    return p

def update(
    beatmap_file: str,
    beatmap_id: int,
    user_id: int,
    set_id: int,
    count: int = 1
) -> None:
    with app.session.database.session as session:
        updated = session.query(DBPlay) \
            .filter(DBPlay.beatmap_id == beatmap_id) \
            .filter(DBPlay.user_id == user_id) \
            .update({
                'count': DBPlay.count + count
            })

        if not updated:
            create(
                beatmap_file,
                beatmap_id,
                user_id,
                set_id,
                count
            )

        session.commit()

def fetch_count_for_beatmap(beatmap_id: int) -> int:
    count = app.session.database.pool_session.query(
        func.sum(DBPlay.count).label('playcount')) \
            .group_by(DBPlay.beatmap_id) \
            .filter(DBPlay.beatmap_id == beatmap_id) \
            .first()

    return count[0] if count else 0
