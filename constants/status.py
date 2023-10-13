
from enum import IntEnum

class DatabaseStatus(IntEnum):
    Graveyard = -2
    WIP       = -1
    Pending   = 0
    Ranked    = 1
    Approved  = 2
    Qualified = 3
    Loved     = 4

class SubmissionStatus(IntEnum):
    NotSubmitted   = -1
    Pending        = 0
    Unknown        = 1
    EditableCutoff = 2
    Approved       = 3
    Ranked         = 4

    @classmethod
    def from_database(cls, status: int):
        return {
            -2: SubmissionStatus.Pending,        # Graveyard
            -1: SubmissionStatus.EditableCutoff, # WIP
            0:  SubmissionStatus.Pending,        # Pending
            1:  SubmissionStatus.Ranked,         # Ranked
            2:  SubmissionStatus.Approved,       # Approved
            3:  SubmissionStatus.Ranked,         # Qualified
            4:  SubmissionStatus.Approved        # Loved
        }[status]

class LegacyStatus(IntEnum):
    NotSubmitted = -1
    Pending      = 0
    Unknown      = 1
    Ranked       = 2

    @classmethod
    def from_database(cls, status: int):
        return {
            -2: LegacyStatus.Pending, # Graveyard
            -1: LegacyStatus.Ranked,  # WIP
            0:  LegacyStatus.Pending, # Pending
            1:  LegacyStatus.Ranked,  # Ranked
            2:  LegacyStatus.Ranked,  # Approved
            3:  LegacyStatus.Ranked,  # Qualified
            4:  LegacyStatus.Ranked   # Loved
        }[status]
