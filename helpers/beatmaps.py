
from __future__ import annotations

from app.common.database import DBBeatmapset, DBBeatmap
from app.common.database.repositories import wrapper
from app.common import officer

from sqlalchemy.orm import Session
from sqlalchemy import func

import config
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

def decrypt_on_fail(e: Exception) -> None:
    officer.call(f'Failed to decrypt osz file: "{e}"')

@wrapper.exception_wrapper(decrypt_on_fail)
def decrypt_osz2(osz2_file: bytes) -> dict | None:
    if not config.OSZ2_SERVICE_URL:
        return

    response = app.session.requests.post(
        f'{config.OSZ2_SERVICE_URL}/osz2/decrypt',
        files={'osz2': osz2_file}
    )

    if not response.ok:
        officer.call(f'Failed to decrypt osz2 file: "{response.text}"')
        return

    return response.json()

@wrapper.exception_wrapper(decrypt_on_fail)
def patch_osz2(patch_file: bytes, osz2: bytes) -> bytes | None:
    if not config.OSZ2_SERVICE_URL:
        return

    response = app.session.requests.post(
        f'{config.OSZ2_SERVICE_URL}/osz2/patch',
        files={
            'patch': patch_file,
            'osz2': osz2
        }
    )

    if not response.ok:
        officer.call(f'Failed to patch osz2 file: "{response.text}"')
        return

    return response.json()
