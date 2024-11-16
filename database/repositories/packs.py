
from __future__ import annotations

from app.common.database.objects import DBBeatmapPack, DBBeatmapPackEntry
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    name: str,
    category: str,
    creator_id: int,
    download_link: str,
    description: str = "",
    beatmapset_ids: List[int] = [],
    session: Session = ...
) -> DBBeatmapPack:
    session.add(
        p := DBBeatmapPack(
            name=name,
            category=category,
            creator_id=creator_id,
            download_link=download_link,
            description=description
        )
    )
    session.commit()
    session.refresh(p)

    add_entries(
        p.id,
        *beatmapset_ids,
        session=session
    )

@session_wrapper
def update(
    id: int,
    updates: dict,
    session: Session = ...
) -> int:
    updates.update({'updated_at': datetime.now()})
    updated = session.query(DBBeatmapPack) \
        .filter(DBBeatmapPack.id == id) \
        .update(updates)
    session.commit()
    return updated

@session_wrapper
def delete(
    id: int,
    session: Session = ...
) -> int:
    deleted = session.query(DBBeatmapPackEntry) \
        .filter(DBBeatmapPackEntry.pack_id == id) \
        .delete()
    deleted += session.query(DBBeatmapPack) \
        .filter(DBBeatmapPack.id == id) \
        .delete()
    session.commit()
    return deleted

@session_wrapper
def fetch_one(
    id: int,
    session: Session = ...
) -> DBBeatmapPack:
    return session.query(DBBeatmapPack) \
        .filter(DBBeatmapPack.id == id) \
        .first()

@session_wrapper
def fetch_all(
    session: Session = ...
) -> List[DBBeatmapPack]:
    return session.query(DBBeatmapPack) \
        .all()

@session_wrapper
def fetch_by_category(
    category: str,
    session: Session = ...
) -> List[DBBeatmapPack]:
    return session.query(DBBeatmapPack) \
        .filter(DBBeatmapPack.category.ilike(category)) \
        .all()

@session_wrapper
def fetch_categories(session: Session = ...) -> List[str]:
    categories = session.query(DBBeatmapPack.category) \
        .distinct() \
        .all()
    return [category[0] for category in categories]

@session_wrapper
def add_entries(
    pack_id: int,
    *beatmapset_ids,
    session: Session = ...
) -> DBBeatmapPackEntry:
    entries = [
        DBBeatmapPackEntry(
            pack_id=pack_id,
            beatmapset_id=beatmapset_id
        )
        for beatmapset_id in beatmapset_ids
    ]
    session.add_all(entries)
    session.commit()
    return entries

@session_wrapper
def remove_entries(
    pack_id: int,
    *beatmapset_ids,
    session: Session = ...
) -> int:
    deleted = session.query(DBBeatmapPackEntry) \
        .filter(DBBeatmapPackEntry.pack_id == pack_id) \
        .filter(DBBeatmapPackEntry.beatmapset_id.in_(beatmapset_ids)) \
        .delete(synchronize_session=False)
    session.commit()
    return deleted

@session_wrapper
def fetch_entries(
    pack_id: int,
    session: Session = ...
) -> List[DBBeatmapPackEntry]:
    return session.query(DBBeatmapPackEntry) \
        .filter(DBBeatmapPackEntry.pack_id == pack_id) \
        .all()
