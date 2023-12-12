
from ..constants import ClientStatus, GameMode, Mods
from ..objects import bStatusUpdate

from typing import Optional
from copy import copy

import app

def update(player_id: int, status: bStatusUpdate, client_hash: str) -> None:
    status = copy(status)

    for key, value in {
        'beatmap_checksum': status.beatmap_checksum,
        'beatmap_id': status.beatmap_id,
        'action': status.action.value,
        'mods': status.mods.value,
        'mode': status.mode.value,
        'hash': client_hash,
        'text': status.text
    }.items():
        app.session.redis.hset(
            f'bancho:status:{player_id}',
            key, value
        )

def get(player_id: int) -> Optional[bStatusUpdate]:
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

def client_hash(player_id: int) -> Optional[str]:
    hash = app.session.redis.hget(
        f'bancho:status:{player_id}',
        'hash'
    )

    if not hash:
        return

    return hash.decode()

def delete(player_id: int) -> None:
    app.session.redis.hdel(
        f'bancho:status:{player_id}',
        'action', 'mode', 'mods', 'text', 'beatmap_id', 'beatmap_checksum', 'hash'
    )

def exists(player_id: int) -> bool:
    return app.session.redis.exists(
        f'bancho:status:{player_id}'
    )
