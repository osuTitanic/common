
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
