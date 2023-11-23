
from app.common.database.objects import DBBeatmap
from sqlalchemy.orm import selectinload
from sqlalchemy import func

from typing import Optional, List
from datetime import datetime

import app

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
    diff: float
) -> DBBeatmap:
    with app.session.database.managed_session() as session:
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

def fetch_by_id(id: int) -> Optional[DBBeatmap]:
    return app.session.database.session.query(DBBeatmap) \
                .options(selectinload(DBBeatmap.beatmapset)) \
                .filter(DBBeatmap.id == id) \
                .first()

def fetch_by_file(filename: str) -> Optional[DBBeatmap]:
    return app.session.database.session.query(DBBeatmap) \
                .options(selectinload(DBBeatmap.beatmapset)) \
                .filter(DBBeatmap.filename == filename) \
                .first()

def fetch_by_checksum(checksum: str) -> Optional[DBBeatmap]:
    return app.session.database.session.query(DBBeatmap) \
                .options(selectinload(DBBeatmap.beatmapset)) \
                .filter(DBBeatmap.md5 == checksum) \
                .first()

def fetch_by_set(set_id: int) -> List[DBBeatmap]:
    return app.session.database.session.query(DBBeatmap) \
                .filter(DBBeatmap.set_id == set_id) \
                .all()

def fetch_count() -> int:
    return app.session.database.session \
            .query(func.count(DBBeatmap.id)) \
            .scalar()

def update(beatmap_id: int, updates: dict) -> int:
    with app.session.database.managed_session() as session:
        rows = session.query(DBBeatmap) \
            .filter(DBBeatmap.id == beatmap_id) \
            .update(updates)
        session.commit()

    return rows
