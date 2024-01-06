
from __future__ import annotations

from ..constants import ClientStatus, GameMode, Mods
from ..objects import bStatusUpdate
from copy import copy

import app

def update(player_id: int, status: bStatusUpdate, client_hash: str, version: int) -> None:
    status = copy(status)

    for key, value in {
        'beatmap_checksum': status.beatmap_checksum,
        'beatmap_id': status.beatmap_id,
        'action': status.action.value,
        'mods': status.mods.value,
        'mode': status.mode.value,
        'hash': client_hash,
        'text': status.text,
        'version': version,
    }.items():
        app.session.redis.hset(
            f'bancho:status:{player_id}',
            key, value
        )

def get(player_id: int) -> bStatusUpdate | None:
    status = app.session.redis.hgetall(
        f'bancho:status:{player_id}'
    )

    if not status:
        return

    return bStatusUpdate(
        action=ClientStatus(int(status[b'action'])),
        mode=GameMode(int(status[b'mode'])),
        mods=Mods(int(status[b'mods'])),
        beatmap_id=int(status[b'beatmap_id']),
        beatmap_checksum=status[b'beatmap_checksum'],
        text=status[b'text'].decode(),
    )

def get_all() -> list[str]:
    return [
        key.decode()
        for key in app.session.redis.keys('bancho:status:*')
    ]

def client_hash(player_id: int) -> str | None:
    hash = app.session.redis.hget(
        f'bancho:status:{player_id}',
        'hash'
    )

    if not hash:
        return

    return hash.decode()

def version(player_id: int) -> int | None:
    version = app.session.redis.hget(
        f'bancho:status:{player_id}',
        'version'
    )

    if not version:
        return

    return int(version)

def delete(player_id: int) -> None:
    app.session.redis.hdel(
        f'bancho:status:{player_id}',
        'action', 'mode', 'mods', 'text', 'beatmap_id', 'beatmap_checksum', 'hash', 'version'
    )

def exists(player_id: int) -> bool:
    return app.session.redis.exists(
        f'bancho:status:{player_id}'
    )
