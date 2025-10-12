
from __future__ import annotations

from app.common.database.objects import DBBeatmapNomination, DBBeatmapset
from sqlalchemy.orm import Session, selectinload

from .wrapper import session_wrapper

@session_wrapper
def create(
    beatmapset_id: int,
    user_id: int,
    session: Session = ...
) -> DBBeatmapNomination:
    session.add(
        nomination := DBBeatmapNomination(
            user_id,
            beatmapset_id
        )
    )
    session.commit()
    session.refresh(nomination)
    return nomination

@session_wrapper
def delete(
    beatmapset_id: int,
    user_id: int,
    session: Session = ...
) -> None:
    session.query(DBBeatmapNomination) \
        .filter(DBBeatmapNomination.user_id == user_id) \
        .filter(DBBeatmapNomination.set_id == beatmapset_id) \
        .delete()
    session.commit()

@session_wrapper
def delete_all(
    beatmapset_id: int,
    session: Session = ...
) -> None:
    session.query(DBBeatmapNomination) \
        .filter(DBBeatmapNomination.set_id == beatmapset_id) \
        .delete()
    session.commit()

@session_wrapper
def count(
    beatmapset_id: int,
    session: Session = ...
) -> int:
    return session.query(DBBeatmapNomination) \
        .filter(DBBeatmapNomination.set_id == beatmapset_id) \
        .count()

@session_wrapper
def fetch_one(
    beatmapset_id: int,
    user_id: int,
    session: Session = ...
) -> DBBeatmapNomination | None:
    return session.query(DBBeatmapNomination) \
        .filter(DBBeatmapNomination.user_id == user_id) \
        .filter(DBBeatmapNomination.set_id == beatmapset_id) \
        .first()

@session_wrapper
def fetch_by_beatmapset(
    beatmapset_id: int,
    session: Session = ...
) -> list[DBBeatmapNomination]:
    return session.query(DBBeatmapNomination) \
        .filter(DBBeatmapNomination.set_id == beatmapset_id) \
        .all()

@session_wrapper
def fetch_by_user(
    user_id: int,
    session: Session = ...
) -> list[DBBeatmapNomination]:
    return session.query(DBBeatmapNomination) \
        .options(selectinload(DBBeatmapNomination.beatmapset)) \
        .filter(DBBeatmapNomination.user_id == user_id) \
        .order_by(DBBeatmapNomination.time.desc()) \
        .all()

@session_wrapper
def fetch_by_user_and_server(
    user_id: int,
    server: int,
    session: Session = ...
) -> list[DBBeatmapNomination]:
    return session.query(DBBeatmapNomination) \
        .join(DBBeatmapNomination.beatmapset) \
        .options(selectinload(DBBeatmapNomination.beatmapset)) \
        .filter(DBBeatmapNomination.user_id == user_id) \
        .filter(DBBeatmapset.server == server) \
        .order_by(DBBeatmapNomination.time.desc()) \
        .all()
