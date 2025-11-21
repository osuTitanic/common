
from ..database.objects import DBScore
from ..streams import StreamOut
from ..constants import Mods

from datetime import datetime, timedelta
import hashlib

def get_ticks(dt: datetime) -> int:
    dt = dt.replace(tzinfo=None)
    return int((dt - datetime(1, 1, 1)).total_seconds() * 10000000)

def decode_ticks(ticks: int) -> datetime:
    return (
        datetime(1, 1, 1) +
        timedelta(microseconds=ticks // 10)
    )

def compute_offline_score_checksum(score: DBScore) -> str:
    return hashlib.md5(
        '{0}p{1}o{2}o{3}t{4}a{5}r{6}e{7}y{8}o{9}u{10}{11}{12}'.format(
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
            score.passed
        ).encode()
    ).hexdigest()

def serialize_replay(score: DBScore, replay: bytes) -> bytes:
    mods = Mods(score.mods)

    if Mods.Nightcore in mods and Mods.DoubleTime not in mods:
        # NC requires DT to be present
        score.mods |= Mods.DoubleTime.value

    stream = StreamOut()
    stream.u8(score.mode)
    stream.s32(score.client_version)
    stream.string(score.beatmap.md5)
    stream.string(score.user.name)
    stream.string(compute_offline_score_checksum(score))
    stream.u16(score.n300)
    stream.u16(score.n100)
    stream.u16(score.n50)
    stream.u16(score.nGeki)
    stream.u16(score.nKatu)
    stream.u16(score.nMiss)
    stream.u32(score.total_score)
    stream.u16(score.max_combo)
    stream.bool(score.perfect)
    stream.u32(score.mods)
    stream.string('') # TODO: HP Graph
    stream.s64(get_ticks(score.submitted_at))
    stream.u32(len(replay))
    stream.write(replay)

    if score.client_version >= 20140721:
        stream.u64(score.id)
    else:
        stream.u32(score.id)

    return stream.get()
