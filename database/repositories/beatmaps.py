
from __future__ import annotations

from app.common.database.objects import DBBeatmap, DBScore
from sqlalchemy.orm import selectinload
from sqlalchemy import func

from .wrapper import session_wrapper

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session

@session_wrapper
def create(
    id: int,
    set_id: int,
    mode: int = 0,
    md5: str = '',
    status: int = -3,
    version: str = '',
    filename: str = '',
    total_length: int = 0,
    max_combo: int = 0,
    bpm: float = 0.0,
    cs: float = 0.0,
    ar: float = 0.0,
    od: float = 0.0,
    hp: float = 0.0,
    diff: float = 0.0,
    submit_date: datetime | None = None,
    last_update: datetime | None = None,
    session: Session = ...
) -> DBBeatmap:
    session.add(
        m := DBBeatmap(
            id=id,
            set_id=set_id,
            mode=mode,
            md5=md5,
            status=status,
            version=version,
            filename=filename,
            created_at=submit_date or datetime.now(),
            last_update=last_update or datetime.now(),
            total_length=total_length,
            max_combo=max_combo,
            bpm=bpm,
            cs=cs,
            ar=ar,
            od=od,
            hp=hp,
            diff=diff
        )
    )
    session.commit()
    session.refresh(m)
    return m

@session_wrapper
def fetch_by_id(id: int, session: Session = ...) -> DBBeatmap | None:
    return session.query(DBBeatmap) \
        .options(selectinload(DBBeatmap.beatmapset)) \
        .filter(DBBeatmap.id == id) \
        .first()

@session_wrapper
def fetch_by_file(filename: str, session: Session = ...) -> DBBeatmap | None:
    return session.query(DBBeatmap) \
        .options(selectinload(DBBeatmap.beatmapset)) \
        .filter(DBBeatmap.filename == filename) \
        .first()

@session_wrapper
def fetch_by_checksum(checksum: str, session: Session = ...) -> DBBeatmap | None:
    return session.query(DBBeatmap) \
        .options(selectinload(DBBeatmap.beatmapset)) \
        .filter(DBBeatmap.md5 == checksum) \
        .first()

@session_wrapper
def fetch_by_set(set_id: int, session: Session = ...) -> List[DBBeatmap]:
    return session.query(DBBeatmap) \
        .filter(DBBeatmap.set_id == set_id) \
        .all()

@session_wrapper
def fetch_count(session: Session = ...) -> int:
    return session.query(func.count(DBBeatmap.id)) \
                  .scalar()

@session_wrapper
def fetch_count_by_mode(mode: int, session: Session = ...) -> int:
    return session.query(func.count(DBBeatmap.id)) \
                  .filter(DBBeatmap.mode == mode) \
                  .scalar()

@session_wrapper
def fetch_count_grouped_status(mode: int, session: Session = ...) -> Dict[int, int]:
    result = session.query(DBBeatmap.status, func.count(DBBeatmap.id)) \
        .filter(DBBeatmap.mode == mode) \
        .group_by(DBBeatmap.status) \
        .all()

    return {status: count for status, count in result}

@session_wrapper
def fetch_count_with_leaderboards(mode: int, session: Session = ...) -> int:
    modes = [mode]

    if mode > 0:
        # Account for converts
        modes.append(0)

    return session.query(func.count(DBBeatmap.id)) \
                  .filter(DBBeatmap.mode.in_(modes)) \
                  .filter(DBBeatmap.status > 0) \
                  .scalar()

@session_wrapper
def fetch_id_by_filename(filename: str, session: Session = ...) -> int | None:
    return session.query(DBBeatmap.id) \
        .filter(DBBeatmap.filename == filename) \
        .scalar()

@session_wrapper
def fetch_filename_by_id(beatmap_id: int, session: Session = ...) -> str | None:
    return session.query(DBBeatmap.filename) \
        .filter(DBBeatmap.id == beatmap_id) \
        .scalar()

@session_wrapper
def fetch_most_played(limit: int = 5, session: Session = ...) -> List[DBBeatmap]:
    return session.query(DBBeatmap) \
        .order_by(DBBeatmap.playcount.desc()) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_most_played_approved(limit: int = 5, session: Session = ...) -> List[DBBeatmap]:
    return session.query(DBBeatmap) \
        .filter(DBBeatmap.status > 0) \
        .order_by(DBBeatmap.playcount.desc()) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_most_played_delta(
    limit: int = 5,
    delta: timedelta = timedelta(hours=24),
    session: Session = ...
) -> List[Tuple[int, DBBeatmap]]:
    time_threshold = datetime.now() - delta

    # Subquery to count scores per beatmap in the last delta
    subquery = session.query(
            DBScore.beatmap_id,
            func.count(DBScore.id).label('play_count')
        ) \
        .filter(DBScore.submitted_at >= time_threshold) \
        .filter(DBScore.hidden == False) \
        .group_by(DBScore.beatmap_id) \
        .subquery()

    # Join with beatmaps and order by play count
    return session.query(
            subquery.c.play_count,
            DBBeatmap
        ) \
        .join(DBBeatmap, DBBeatmap.id == subquery.c.beatmap_id) \
        .options(selectinload(DBBeatmap.beatmapset)) \
        .order_by(subquery.c.play_count.desc()) \
        .limit(limit) \
        .all()

@session_wrapper
def update(
    beatmap_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBBeatmap) \
        .filter(DBBeatmap.id == beatmap_id) \
        .update(updates)
    session.commit()
    return rows

@session_wrapper
def exists(beatmap_id: int, session: Session = ...) -> bool:
    return session.query(DBBeatmap.id) \
        .filter(DBBeatmap.id == beatmap_id) \
        .scalar() is not None

@session_wrapper
def filename_exists(filename: str, session: Session = ...) -> bool:
    return session.query(DBBeatmap.id) \
        .filter(DBBeatmap.filename == filename) \
        .scalar() is not None

@session_wrapper
def update_by_set_id(
    set_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBBeatmap) \
        .filter(DBBeatmap.set_id == set_id) \
        .update(updates)
    session.commit()
    return rows

@session_wrapper
def delete_by_id(id: int, session: Session = ...) -> int:
    rows = session.query(DBBeatmap) \
        .filter(DBBeatmap.id == id) \
        .delete()
    session.commit()
    return rows

@session_wrapper
def delete_by_set_id(set_id: int, session: Session = ...) -> int:
    rows = session.query(DBBeatmap) \
        .filter(DBBeatmap.set_id == set_id) \
        .delete()
    session.commit()
    return rows
