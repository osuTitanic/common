
from __future__ import annotations
from typing import List

from app.common.database.objects import DBPlay
from sqlalchemy.orm import Session
from sqlalchemy import func

from .wrapper import session_wrapper

@session_wrapper
def create(
    beatmap_file: str,
    beatmap_id: int,
    user_id: int,
    set_id: int,
    count: int = 1,
    session: Session = ...
) -> DBPlay:
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
    session.refresh(p)
    return p

@session_wrapper
def update(
    beatmap_file: str,
    beatmap_id: int,
    user_id: int,
    set_id: int,
    count: int = 1,
    session: Session = ...
) -> None:
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

@session_wrapper
def fetch_count_for_beatmap(beatmap_id: int, session: Session = ...) -> int:
    count = session.query(
        func.sum(DBPlay.count).label('playcount')) \
            .group_by(DBPlay.beatmap_id) \
            .filter(DBPlay.beatmap_id == beatmap_id) \
            .first()

    return count[0] if count else 0
    
@session_wrapper
def fetch_most_played_by_user(
    user_id: int,
    limit: int = 15,
    offset: int = 0,
    session: Session = ...
) -> List[DBPlay]:
    return session.query(DBPlay) \
        .filter(DBPlay.user_id == user_id) \
        .order_by(DBPlay.count.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def delete_by_id(id: int, session: Session = ...) -> int:
    rows = session.query(DBPlay) \
        .filter(DBPlay.id == id) \
        .delete()
    session.commit()
    return rows

@session_wrapper
def delete_by_set_id(set_id: int, session: Session = ...) -> int:
    rows = session.query(DBPlay) \
        .filter(DBPlay.set_id == set_id) \
        .delete()
    session.commit()
    return rows

@session_wrapper
def delete_by_beatmap_id(beatmap_id: int, session: Session = ...) -> int:
    rows = session.query(DBPlay) \
        .filter(DBPlay.beatmap_id == beatmap_id) \
        .delete()
    session.commit()
    return rows
