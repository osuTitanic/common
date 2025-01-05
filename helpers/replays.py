
from ..database.objects import DBScore
from datetime import datetime
import hashlib

def get_ticks(dt: datetime) -> int:
    dt = dt.replace(tzinfo=None)
    return int((dt - datetime(1, 1, 1)).total_seconds() * 10000000)

def decode_ticks(ticks: int) -> datetime:
    return (
        datetime.datetime(1, 1, 1) +
        datetime.timedelta(microseconds=ticks // 10)
    )

def compute_online_score_checksum(score: DBScore, storyboard_checksum=None) -> str:
    if score.client_version >= 20140715:
        return compute_score_checksum_latest(
            score,
            storyboard_checksum
        )

    return compute_score_checksum_2012(score)

def compute_score_checksum_latest(score: DBScore, storyboard_checksum: str) -> str:
    return hashlib.md5(
        "chickenmcnuggets{0}o15{1}{2}smustard{3}{4}uu{5}{6}{7}{8}{9}{10}{11}Q{12}{13}{15}{14:%y%m%d%H%M%S}{16}{17}".format(
            score.n100 + score.n300,
            score.n50,
            score.ngeki,
            score.nkatu,
            score.nmiss,
            score.beatmap.md5,
            score.max_combo,
            score.perfect,
            score.user.name,
            score.total_score,
            score.grade.name,
            int(score.mods),
            (not score.failtime),
            score.mode.value,
            score.submitted_at.strftime("%y%m%d%H%M%S"),
            score.client_version,
            score.client_hash,
            storyboard_checksum
        ).encode()
    ).hexdigest()

def compute_score_checksum_2012(score: DBScore) -> str:
    return hashlib.md5(
        "poop{0}o15{1}{2}s{3}{4}uu{5}{6}{7}{8}{9}{10}{11}Q{12}{13}{15}{14:yyMMddHHmmss}{16}".format(
            score.n100 + score.n300,
            score.n50,
            score.ngeki,
            score.nkatu,
            score.nmiss,
            score.beatmap.md5,
            score.max_combo,
            score.perfect,
            score.user.name,
            score.total_score,
            score.grade.name,
            score.mods,
            score.passed,
            score.mode.value,
            score.submitted_at.strftime("%y%m%d%H%M%S"),
            score.client_version,
            score.client_hash
        ).encode()
    ).hexdigest()

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
