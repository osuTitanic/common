
from enum import Enum, IntEnum

class CommentTarget(str, Enum):
    Replay = 'replay'
    Song   = 'song'
    Map    = 'map'

class RankingType(IntEnum):
    Local       = 0
    Top         = 1
    SelectedMod = 2
    Friends     = 3
    Country     = 4

class ScoreStatus(IntEnum):
    Hidden    = -1
    Failed    = 0
    Exited    = 1
    Submitted = 2
    Best      = 3
    Mods      = 4

class DirectDisplayMode(IntEnum):
    """Search category for osu!direct"""
    Ranked       = 0
    RankedStrict = 1
    Pending      = 2
    Qualified    = 3
    All          = 4
    Graveyard    = 5
    Approved     = 6
    RankedPlayed = 7
    Loved        = 8
