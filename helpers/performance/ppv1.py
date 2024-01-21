
from __future__ import annotations

from ...database.repositories import scores, wrapper
from ...database.objects import DBScore, DBBeatmap
from ...constants import Mods

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List

import math
import app

# ppv1 reference: https://gist.github.com/peppy/4f8fcb6629d300c56ebe80156b20b76c

def calculate_star_rating(beatmap: DBBeatmap) -> float:
    """Calculate the old eyup star rating"""
    # TODO: Add an actual implementation
    return min(5, beatmap.diff * 0.565)

def calculate_ppv1(score: DBScore, session: Session | None = None) -> float:
    """Calculate ppv1, by using the score's pp as a difficulty factor"""
    if score.beatmap.playcount <= 0:
        return 0

    score_rank = scores.fetch_score_index_by_tscore(
        score.total_score,
        score.beatmap.id,
        score.mode,
        session=session
    )

    mods = Mods(score.mods)

    # TODO: Use old eyup star rating
    star_rating = calculate_star_rating(score.beatmap)

    base_pp = math.pow(star_rating, 4) / math.pow(score_rank, 0.5)

    # Older scores will give less pp
    score_age = (datetime.now() - score.submitted_at.replace(tzinfo=None)).days
    age_factor = max(0.01, 1 - 0.01 * (score_age / 10))

    # Bonus for SS's & FC's
    ss_bonus = 1.36 if score.acc == 1 else 1
    fc_bonus = 1.2 if score.perfect and score.acc != 1 else 1

    # Adjustments for mods
    hr_bonus = 1.1 if (Mods.HardRock in mods) else 1
    dt_bonus = 1.1 if (Mods.DoubleTime in mods) or (Mods.Nightcore in mods) else 1
    rx_nerf  = 0.6 if (Mods.Relax in mods) or (Mods.Autopilot in mods) else 1
    ez_nerf  = 0.2 if (Mods.Easy in mods) or (Mods.HalfTime in mods) else 1

    # NOTE: Beatmap popularity is nefed a LOT, since it would inflate pp to the roof
    populariy_factor = math.pow(score.beatmap.playcount, 0.145)
    acc_factor = math.pow(score.acc, 15)

    # Nerf converts
    if score.mode > 0 and score.mode != score.beatmap.mode:
        base_pp *= 0.2

    # Nerf "easy maps"... idk?
    if score.mode != 1 and (score.beatmap.passcount / score.beatmap.playcount) > 0.3:
        base_pp *= 0.2

    result_pp = math.prod([
        base_pp,
        age_factor,
        ss_bonus,
        fc_bonus,
        hr_bonus,
        dt_bonus,
        rx_nerf,
        ez_nerf,
        populariy_factor,
        acc_factor
    ])

    return max(0, result_pp)

def calculate_weight(pps: List[float]) -> float:
    """Calculate the sum of weighted pp for each score"""
    pps.sort(reverse=True)
    return sum(pp * 0.95**index for index, pp in enumerate(pps))

@wrapper.session_wrapper
def calculate_weighted_ppv1(
    scores: List[DBScore],
    session: Session | None = None
) -> float:
    """Calculate weighted ppv1 with from a list of scores"""
    return calculate_weight([
        calculate_ppv1(
            score,
            session
        )
        for score in scores
    ])
