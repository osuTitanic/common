
from enum import IntEnum

class BeatmapStatus(IntEnum):
    Inactive  = -3
    Graveyard = -2
    WIP       = -1
    Pending   = 0
    Ranked    = 1
    Approved  = 2
    Qualified = 3
    Loved     = 4

    @classmethod
    def values(cls) -> list:
        return list(cls._value2member_map_.keys())

    @classmethod
    def from_lowercase(cls, status: str):
        return {
            'inactive':  cls.Inactive,
            'graveyard': cls.Graveyard,
            'wip':       cls.WIP,
            'pending':   cls.Pending,
            'ranked':    cls.Ranked,
            'approved':  cls.Approved,
            'qualified': cls.Qualified,
            'loved':     cls.Loved
        }.get(status, None)

class BeatmapGenre(IntEnum):
    Any = 0
    Unspecified = 1
    VideoGame = 2
    Anime = 3
    Rock = 4
    Pop = 5
    Other = 6
    Novelty = 7
    HipHop = 9
    Electronic = 10
    Metal = 11
    Classical = 12
    Folk = 13
    Jazz = 14

    @classmethod
    def values(cls) -> list:
        return list(cls._value2member_map_.keys())

class BeatmapLanguage(IntEnum):
    Any = 0
    Unspecified = 1
    English = 2
    Japanese = 3
    Chinese = 4
    Instrumental = 5
    Korean = 6
    French = 7
    German = 8
    Swedish = 9
    Spanish = 10
    Italian = 11
    Russian = 12
    Polish = 13
    Other = 14

    @classmethod
    def values(cls) -> list:
        return list(cls._value2member_map_.keys())

class BeatmapSortBy(IntEnum):
    Title = 0
    Artist = 1
    Creator = 2
    Difficulty = 3
    Ranked = 4
    Rating = 5
    Plays = 6
    Created = 7
    Relevance = 8

    @classmethod
    def values(cls) -> list:
        return list(cls._value2member_map_.keys())

class BeatmapCategory(IntEnum):
    Any = 0
    Leaderboard = 1
    Ranked = 2
    Qualified = 3
    Loved = 4
    Approved = 5
    Pending = 6
    WIP = 7
    Graveyard = 8

    @classmethod
    def values(cls) -> list:
        return list(cls._value2member_map_.keys())

class BeatmapOrder(IntEnum):
    Descending = 0
    Ascending = 1

    @classmethod
    def values(cls) -> list:
        return list(cls._value2member_map_.keys())
