
from ..database.objects import DBScore
from datetime import datetime

import hashlib

def compute_score_checksum(score: DBScore) -> str:
    return hashlib.md5(
        '{}p{}o{}o{}t{}a{}r{}e{}y{}o{}u{}{}{}'.format(
            (score.n100 + score.n300),
            score.n50,
            score.nGeki,
            score.nKatu,
            score.nMiss,
            score.beatmap.md5,
            score.max_combo,
            score.perfect,
            score.user.name,
            score.total_score,
            score.grade,
            score.mods,
            (not score.failtime) # (passed)
        ).encode()
    ).hexdigest()

def get_ticks(dt: datetime) -> int:
    dt = dt.replace(tzinfo=None)
    return int((dt - datetime(1, 1, 1)).total_seconds() * 10000000)

def decode_ticks(ticks: int) -> datetime:
    return (
        datetime.datetime(1, 1, 1) +
        datetime.timedelta(microseconds=ticks // 10)
    )
