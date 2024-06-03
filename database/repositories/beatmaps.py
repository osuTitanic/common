
from __future__ import annotations

from app.common.database.objects import DBBeatmap, DBBeatmapset
from app.common.constants.status import DatabaseStatus
from app.common.webhooks import Embed, Image, Author

from sqlalchemy.orm import selectinload
from sqlalchemy import func

from .wrapper import session_wrapper

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

import app.common
import config
import app

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
            id,
            set_id,
            mode,
            md5,
            status,
            version,
            filename,
            submit_date or datetime.now(),
            last_update or datetime.now(),
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
def update(
    beatmap_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBBeatmap) \
        .filter(DBBeatmap.id == beatmap_id) \
        .update(updates)
    post_beatmap_change(session.query(DBBeatmap).filter(DBBeatmap.id == beatmap_id).first())
    session.commit()
    return rows

@session_wrapper
def update_by_set_id(
    set_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBBeatmap) \
        .filter(DBBeatmap.set_id == set_id) \
        .update(updates)
    post_beatmapset_change(session.get(DBBeatmapset, set_id))
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

def post_beatmapset_change(beatmapset: DBBeatmapset):
    status_name = [status.name for status in DatabaseStatus if status.value == beatmapset.status][0]

    embed = Embed(title=f'Status change: {beatmapset.title}')
    embed.image = Image(url=f'https://assets.ppy.sh/beatmaps/{beatmapset.id}/covers/cover.jpg')
    embed.author = Author(name="New beatmapset update!")
    embed.add_field(name="Artist", value=beatmapset.artist, inline=True)
    embed.add_field(name="Creator", value=beatmapset.creator, inline=True)
    embed.add_field(name="New status", value=status_name, inline=True)
    embed.add_field(name="Bancho url", value=f"https://osu.ppy.sh/s/{beatmapset.id}", inline=True)
    embed.add_field(name="Titanic url", value=f"https://{config.DOMAIN_NAME}/s/{beatmapset.id}", inline=True)
    app.common.officer.event(embeds=[embed])

def post_beatmap_change(beatmap: DBBeatmap):
    beatmapset = beatmap.beatmapset
    status_name = [status.name for status in DatabaseStatus if status.value == beatmap.status][0]
    embed = Embed(title=f'Status change: {beatmapset.title} ({beatmap.version})')
    embed.image = Image(url=f'https://assets.ppy.sh/beatmaps/{beatmapset.id}/covers/cover.jpg')
    embed.author = Author(name="New beatmap update!")
    embed.add_field(name="Artist", value=beatmapset.artist, inline=True)
    embed.add_field(name="Creator", value=beatmapset.creator, inline=True)
    embed.add_field(name="New status", value=status_name, inline=True)
    embed.add_field(name="Bancho url", value=f"https://osu.ppy.sh/b/{beatmap.id}", inline=True)
    embed.add_field(name="Titanic url", value=f"https://{config.DOMAIN_NAME}/b/{beatmap.id}", inline=True)
    app.common.officer.event(embeds=[embed])
