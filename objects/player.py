
from __future__ import annotations
from dataclasses import dataclass

from ..constants import (
    ClientStatus,
    Permissions,
    QuitState,
    GameMode,
    Mods
)

@dataclass(slots=True)
class StatusUpdate:
    action: ClientStatus
    text: str = ""
    mods: Mods = Mods.NoMod
    mode: GameMode = GameMode.Osu
    beatmap_checksum: str = ""
    beatmap_id: int = -1

@dataclass(slots=True)
class UserPresence:
    user_id: int
    is_irc: bool
    username: str
    timezone: int
    country_code: int
    permissions: Permissions
    mode: GameMode
    longitude: float
    latitude: float
    rank: int
    city: str | None = None

@dataclass(slots=True)
class UserStats:
    user_id: int
    status: StatusUpdate
    rscore: int
    tscore: int
    accuracy: float
    playcount: int
    rank: int
    pp: int

@dataclass(slots=True)
class UserQuit:
    user_id: int
    presence: UserPresence
    stats: UserStats
    quit_state: QuitState
