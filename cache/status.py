
from __future__ import annotations
from typing import List

from app.common.constants import ClientStatus, GameMode, Mods
from app.common.objects import bStatusUpdate, bUserStats
from copy import copy

import app

def update(
    player_id: int,
    stats: bUserStats,
    status: bStatusUpdate,
    hash: str,
    version: int
) -> None:
    status_update = {
        'beatmap_checksum': status.beatmap_checksum,
        'beatmap_id': status.beatmap_id,
        'action': status.action.value,
        'mods': status.mods.value,
        'mode': status.mode.value,
        'text': status.text,
        'version': version,
        'hash': hash
    }
    stats_update = {
        'rscore': stats.rscore,
        'tscore': stats.tscore,
        'accuracy': stats.accuracy,
        'playcount': stats.playcount,
        'rank': stats.rank,
        'pp': stats.pp,
    }

    with app.session.redis.pipeline() as pipe:
        pipe.hset(f"bancho:status:{player_id}", mapping=status_update)
        pipe.hset(f"bancho:stats:{player_id}", mapping=stats_update)
        pipe.execute()

def get(player_id: int) -> bUserStats | None:
    with app.session.redis.pipeline() as pipe:
        pipe.hgetall(f"bancho:status:{player_id}")
        pipe.hgetall(f"bancho:stats:{player_id}")
        status, stats = pipe.execute()

    if not status or not stats:
        return None

    return bUserStats(
        player_id,
        bStatusUpdate(
            action=ClientStatus(int(status[b'action'])),
            mode=GameMode(int(status[b'mode'])),
            mods=Mods(int(status[b'mods'])),
            beatmap_id=int(status[b'beatmap_id']),
            beatmap_checksum=status[b'beatmap_checksum'].decode(),
            text=status[b'text'].decode(),
        ),
        rscore=int(stats[b'rscore']),
        tscore=int(stats[b'tscore']),
        accuracy=float(stats[b'accuracy']),
        playcount=int(stats[b'playcount']),
        rank=int(stats[b'rank']),
        pp=float(stats[b'pp'])
    )

def get_keys() -> List[str]:
    return [
        key.decode()
        for key in app.session.redis.keys('bancho:status:*')
    ] + [
        key.decode()
        for key in app.session.redis.keys('bancho:stats:*')
    ]

def delete(player_id: int) -> None:
    app.session.redis.hdel(
        f'bancho:status:{player_id}',
        'action', 'mode', 'mods', 'text', 'beatmap_id',
        'beatmap_checksum', 'hash', 'version'
    )
    app.session.redis.hdel(
        f'bancho:stats:{player_id}',
        'rscore', 'tscore', 'accuracy',
        'playcount', 'rank', 'pp'
    )

def exists(player_id: int) -> bool:
    return app.session.redis.exists(
        f'bancho:status:{player_id}'
    )

def version(player_id: int) -> int | None:
    version = app.session.redis.hget(
        f'bancho:status:{player_id}',
        'version'
    )

    if not version:
        return

    return int(version)

def client_hash(player_id: int) -> str | None:
    hash = app.session.redis.hget(
        f'bancho:status:{player_id}',
        'hash'
    )

    if not hash:
        return

    return hash.decode()

def device_id(player_id: int) -> str | None:
    if not (hash := client_hash(player_id)):
        return

    return ':'.join(hash.split(':')[2:])
