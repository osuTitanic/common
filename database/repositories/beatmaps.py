
from __future__ import annotations

from app.common.database.objects import DBBeatmap
from sqlalchemy.orm import selectinload
from sqlalchemy import func

from .wrapper import session_wrapper

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

import app

@session_wrapper
def create(
    id: int,
    set_id: int,
    mode: int,
    md5: str,
    status: int,
    version: str,
    filename: str,
    created_at: datetime,
    last_update: datetime,
    total_length: int,
    max_combo: int,
    bpm: float,
    cs: float,
    ar: float,
    od: float,
    hp: float,
    diff: float,
    session: Session | None = None
) -> DBBeatmap:
    session.add(
        m := DBBeatmap(
            id,
            set_id,
            mode,
            md5,
            status,
            version,
            filename,
            created_at,
            last_update,
            total_length,
            max_combo,
            bpm,
            cs,
            ar,
            od,
            hp,
            diff
        )
    )
    session.commit()
    session.refresh(m)
    return m

@session_wrapper
def fetch_by_id(id: int, session: Session | None = None) -> DBBeatmap | None:
    return session.query(DBBeatmap) \
        .options(selectinload(DBBeatmap.beatmapset)) \
        .filter(DBBeatmap.id == id) \
        .first()

@session_wrapper
def fetch_by_file(filename: str, session: Session | None = None) -> DBBeatmap | None:
    return session.query(DBBeatmap) \
        .options(selectinload(DBBeatmap.beatmapset)) \
        .filter(DBBeatmap.filename == filename) \
        .first()

@session_wrapper
def fetch_by_checksum(checksum: str, session: Session | None = None) -> DBBeatmap | None:
    return session.query(DBBeatmap) \
        .options(selectinload(DBBeatmap.beatmapset)) \
        .filter(DBBeatmap.md5 == checksum) \
        .first()

@session_wrapper
def fetch_by_set(set_id: int, session: Session | None = None) -> List[DBBeatmap]:
    return session.query(DBBeatmap) \
        .filter(DBBeatmap.set_id == set_id) \
        .all()

@session_wrapper
def fetch_count(session: Session | None = None) -> int:
    return session.query(func.count(DBBeatmap.id)) \
                  .scalar()

@session_wrapper
def update(
    beatmap_id: int,
    updates: dict,
    session: Session | None = None
) -> int:
    rows = session.query(DBBeatmap) \
        .filter(DBBeatmap.id == beatmap_id) \
        .update(updates)
    session.commit()
    return rows

@session_wrapper
def update_by_set_id(
    set_id: int,
    updates: dict,
    session: Session | None = None
) -> int:
    rows = session.query(DBBeatmap) \
        .filter(DBBeatmap.set_id == set_id) \
        .update(updates)
    session.commit()
    return rows
