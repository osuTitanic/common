
from app.common.database.objects import DBBeatmapNomination, DBBeatmapset
from sqlalchemy.orm import Session, selectinload

from .wrapper import session_wrapper, SessionProvider

@session_wrapper
def create(
    beatmapset_id: int,
    user_id: int,
    session: Session = SessionProvider
) -> DBBeatmapNomination:
    session.add(
        nomination := DBBeatmapNomination(
            user_id=user_id,
            set_id=beatmapset_id
        )
    )
    session.flush()
    session.refresh(nomination)
    return nomination

@session_wrapper
def delete(
    beatmapset_id: int,
    user_id: int,
    session: Session = SessionProvider
) -> None:
    session.query(DBBeatmapNomination) \
        .filter(DBBeatmapNomination.user_id == user_id) \
        .filter(DBBeatmapNomination.set_id == beatmapset_id) \
        .delete()
    session.flush()

@session_wrapper
def delete_all(
    beatmapset_id: int,
    session: Session = SessionProvider
) -> None:
    session.query(DBBeatmapNomination) \
        .filter(DBBeatmapNomination.set_id == beatmapset_id) \
        .delete()
    session.flush()

@session_wrapper
def count(
    beatmapset_id: int,
    session: Session = SessionProvider
) -> int:
    return session.query(DBBeatmapNomination) \
        .filter(DBBeatmapNomination.set_id == beatmapset_id) \
        .count()

@session_wrapper
def fetch_one(
    beatmapset_id: int,
    user_id: int,
    session: Session = SessionProvider
) -> DBBeatmapNomination | None:
    return session.query(DBBeatmapNomination) \
        .filter(DBBeatmapNomination.user_id == user_id) \
        .filter(DBBeatmapNomination.set_id == beatmapset_id) \
        .first()

@session_wrapper
def fetch_by_beatmapset(
    beatmapset_id: int,
    session: Session = SessionProvider
) -> list[DBBeatmapNomination]:
    return session.query(DBBeatmapNomination) \
        .filter(DBBeatmapNomination.set_id == beatmapset_id) \
        .all()

@session_wrapper
def fetch_by_user(
    user_id: int,
    session: Session = SessionProvider
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
    session: Session = SessionProvider
) -> list[DBBeatmapNomination]:
    return session.query(DBBeatmapNomination) \
        .join(DBBeatmapNomination.beatmapset) \
        .options(selectinload(DBBeatmapNomination.beatmapset)) \
        .filter(DBBeatmapNomination.user_id == user_id) \
        .filter(DBBeatmapset.server == server) \
        .order_by(DBBeatmapNomination.time.desc()) \
        .all()
