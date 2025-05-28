
from __future__ import annotations
from typing import List

from app.common.database.objects import DBPlay, DBBeatmap, DBBeatmapset
from sqlalchemy import func, text, desc
from sqlalchemy.orm import Session

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
def fetch_most_played(limit: int = 5, session: Session = ...) -> List[dict]:
    # Build a subquery that groups only by beatmap_id
    count_subquery = session.query(
            DBPlay.beatmap_id.label("beatmap_id"),
            func.sum(DBPlay.count).label("total_count")
        ) \
        .group_by(DBPlay.beatmap_id) \
        .subquery()

    # Join query back to beatmaps -> beatmapsets to pull in all metadata
    query = session.query(
            count_subquery.c.beatmap_id.label("beatmap_id"),
            DBBeatmapset.id.label("set_id"),
            DBBeatmapset.title,
            DBBeatmapset.artist,
            DBBeatmap.version,
            DBBeatmapset.creator,
            DBBeatmapset.creator_id,
            DBBeatmapset.server,
            count_subquery.c.total_count.label("count"),
        ) \
        .join(DBBeatmap, DBBeatmap.id == count_subquery.c.beatmap_id) \
        .join(DBBeatmapset, DBBeatmapset.id == DBBeatmap.set_id) \
        .order_by(count_subquery.c.total_count.desc()) \
        .limit(limit)

    return [
        {
            "beatmap_id": r.beatmap_id,
            "set_id":      r.set_id,
            "title":       r.title,
            "artist":      r.artist,
            "version":     r.version,
            "creator":     r.creator,
            "creator_id":  r.creator_id,
            "server":      r.server,
            "count":       r.count,
        }
        for r in query.all()
    ]

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
