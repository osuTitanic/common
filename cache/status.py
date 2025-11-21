
from app.common.constants import ClientStatus, GameMode, Mods
from dataclasses import dataclass
from typing import List

import app

@dataclass(slots=True)
class StatusUpdate:
    action: ClientStatus
    text: str = ""
    mods: Mods = Mods.NoMod
    mode: GameMode = GameMode.Osu
    beatmap_checksum: str = ""
    beatmap_id: int = -1

@dataclass(slots=True)
class UserStats:
    user_id: int
    status: StatusUpdate
    rscore: int
    tscore: int
    accuracy: float
    playcount: int
    rank: int
    pp: float

def update(
    player_id: int,
    stats: UserStats,
    status: StatusUpdate,
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

def get(player_id: int) -> UserStats | None:
    with app.session.redis.pipeline() as pipe:
        pipe.hgetall(f"bancho:status:{player_id}")
        pipe.hgetall(f"bancho:stats:{player_id}")
        status, stats = pipe.execute()

    if not status or not stats:
        return None

    return UserStats(
        player_id,
        StatusUpdate(
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
        return None

    return int(version)

def client_hash(player_id: int) -> str | None:
    hash = app.session.redis.hget(
        f'bancho:status:{player_id}',
        'hash'
    )

    if not hash:
        return None

    return hash.decode()

def device_id(player_id: int) -> str | None:
    if not (hash := client_hash(player_id)):
        return None

    return ':'.join(hash.split(':')[2:])
