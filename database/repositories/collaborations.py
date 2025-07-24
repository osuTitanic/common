
from __future__ import annotations

from .wrapper import session_wrapper
from app.common.database.objects import (
    DBBeatmapCollaborationBlacklist,
    DBBeatmapCollaborationRequest,
    DBBeatmapCollaboration,
    DBUser
)

from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

@session_wrapper
def create(
    beatmap_id: int,
    user_id: int,
    is_beatmap_author: bool = False,
    allow_resource_updates: bool = False,
    session: Session = ...
) -> DBBeatmapCollaboration:
    entry = DBBeatmapCollaboration(
        user_id=user_id,
        beatmap_id=beatmap_id,
        created_at=datetime.now(),
        is_beatmap_author=is_beatmap_author,
        allow_resource_updates=allow_resource_updates
    )
    session.add(entry)
    session.commit()
    return entry

@session_wrapper
def create_request(
    user_id: int,
    target_id: int,
    beatmap_id: int,
    session: Session = ...
) -> DBBeatmapCollaborationRequest:
    entry = DBBeatmapCollaborationRequest(
        user_id=user_id,
        target_id=target_id,
        beatmap_id=beatmap_id,
        created_at=datetime.now()
    )
    session.add(entry)
    session.commit()
    return entry

@session_wrapper
def create_blacklist(
    user_id: int,
    target_id: int,
    session: Session = ...
) -> DBBeatmapCollaborationBlacklist:
    entry = DBBeatmapCollaborationBlacklist(
        user_id=user_id,
        target_id=target_id,
        created_at=datetime.now()
    )
    session.add(entry)
    session.commit()
    return entry

@session_wrapper
def fetch_one(
    beatmap_id: int,
    user_id: int,
    session: Session = ...
) -> DBBeatmapCollaboration | None:
    return session.query(DBBeatmapCollaboration) \
        .filter(DBBeatmapCollaboration.beatmap_id == beatmap_id) \
        .filter(DBBeatmapCollaboration.user_id == user_id) \
        .first()

@session_wrapper
def fetch_by_beatmap(beatmap_id: int, session: Session = ...) -> List[DBBeatmapCollaboration]:
    return session.query(DBBeatmapCollaboration) \
        .filter(DBBeatmapCollaboration.beatmap_id == beatmap_id) \
        .all()

@session_wrapper
def fetch_by_user(user_id: int, session: Session = ...) -> List[DBBeatmapCollaboration]:
    return session.query(DBBeatmapCollaboration) \
        .filter(DBBeatmapCollaboration.user_id == user_id) \
        .order_by(DBBeatmapCollaboration.created_at.desc()) \
        .all()

@session_wrapper
def fetch_by_beatmaps(beatmap_ids: List[int], session: Session = ...) -> List[DBBeatmapCollaboration]:
    return session.query(DBBeatmapCollaboration) \
        .filter(DBBeatmapCollaboration.beatmap_id.in_(beatmap_ids)) \
        .all()

@session_wrapper
def fetch_usernames(beatmap_id: int, session: Session = ...) -> List[str]:
    return session.query(DBUser.name) \
        .join(DBBeatmapCollaboration, DBUser.id == DBBeatmapCollaboration.user_id) \
        .filter(DBBeatmapCollaboration.beatmap_id == beatmap_id) \
        .all()

@session_wrapper
def exists(
    beatmap_id: int,
    user_id: int,
    session: Session = ...
) -> bool:
    return session.query(DBBeatmapCollaboration) \
        .filter(DBBeatmapCollaboration.beatmap_id == beatmap_id) \
        .filter(DBBeatmapCollaboration.user_id == user_id) \
        .count() > 0

@session_wrapper
def is_blacklisted(
    user_id: int,
    target_id: int,
    session: Session = ...
) -> bool:
    return session.query(DBBeatmapCollaborationBlacklist) \
        .filter(DBBeatmapCollaborationBlacklist.user_id == user_id) \
        .filter(DBBeatmapCollaborationBlacklist.target_id == target_id) \
        .count() > 0

@session_wrapper
def delete(
    beatmap_id: int,
    user_id: int,
    session: Session = ...
) -> bool:
    deleted_rows = session.query(DBBeatmapCollaboration) \
        .filter(DBBeatmapCollaboration.beatmap_id == beatmap_id) \
        .filter(DBBeatmapCollaboration.user_id == user_id) \
        .delete(synchronize_session=False)
    session.commit()
    return deleted_rows > 0

@session_wrapper
def delete_by_beatmap(
    beatmap_id: int,
    session: Session = ...
) -> None:
    session.query(DBBeatmapCollaboration) \
        .filter(DBBeatmapCollaboration.beatmap_id == beatmap_id) \
        .delete(synchronize_session=False)
    session.commit()
