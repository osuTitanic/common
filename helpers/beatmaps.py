
from app.common.database import DBBeatmapset, DBBeatmap
from app.common.database.repositories import wrapper

from sqlalchemy.orm import Session
from sqlalchemy import func

import app

@wrapper.session_wrapper
def next_beatmapset_id(session: Session = ...) -> int:
    """Get the next availabe beatmapset id"""
    while True:
        database_id = session.query(
            func.nextval('beatmapsets_id_seq')
        ).scalar()

        exists = session.query(DBBeatmapset.id) \
            .filter(DBBeatmapset.id == database_id) \
            .count() > 0

        if exists:
            continue

        # Check if the beatmapset id is already in use on peppy's servers
        response = app.session.requests.head(
            f'https://osu.ppy.sh/beatmapsets/{database_id}'
        )

        if response.status_code != 404:
            continue

        return database_id

@wrapper.session_wrapper
def next_beatmap_id(session: Session = ...) -> int:
    """Get the next availabe beatmap id"""
    while True:
        database_id = session.query(
            func.nextval('beatmaps_id_seq')
        ).scalar()

        exists = session.query(DBBeatmap.id) \
            .filter(DBBeatmap.id == database_id) \
            .count() > 0

        if exists:
            continue

        # Check if the beatmap id is already in use on peppy's servers
        response = app.session.requests.head(
            f'https://osu.ppy.sh/beatmaps/{database_id}'
        )

        if response.status_code != 404:
            continue

        return database_id
