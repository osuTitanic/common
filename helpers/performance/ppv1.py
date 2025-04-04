
from __future__ import annotations

from ...database.repositories import scores, beatmaps, wrapper
from ...database.objects import DBScore, DBBeatmap
from ...constants import Mods

from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

import math

# ppv1 reference: https://gist.github.com/peppy/4f8fcb6629d300c56ebe80156b20b76c

def calculate_star_rating(beatmap: DBBeatmap) -> float:
    """Calculate the old eyup star rating"""
    # TODO: Add an actual implementation
    return min(5, beatmap.diff * 0.565)

@wrapper.session_wrapper
def calculate_ppv1(
    score: DBScore,
    session: Session = ...
) -> float:
    """Calculate ppv1, by using the score's pp as a difficulty factor"""
    beatmap = beatmaps.fetch_by_id(
        score.beatmap_id,
        session=session
    )

    if beatmap.playcount <= 0:
        return 0

    score_rank = scores.fetch_score_index_by_tscore(
        score.total_score,
        beatmap.id,
        score.mode,
        session=session
    )

    mods = Mods(score.mods)

    # TODO: Use old eyup star rating
    star_rating = calculate_star_rating(beatmap)
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
    rx_nerf  = 0.3 if (Mods.Relax in mods) or (Mods.Autopilot in mods) else 1
    ez_nerf  = 0.2 if (Mods.Easy in mods) or (Mods.HalfTime in mods) else 1

    # NOTE: Beatmap popularity is nefed a LOT, since it would inflate pp to the roof
    populariy_factor = math.pow(beatmap.playcount, 0.145)
    acc_factor = math.pow(score.acc, 15)

    # Nerf converts
    if score.mode > 0 and score.mode != beatmap.mode:
        base_pp *= 0.2

    # Nerf "easy maps"... idk?
    if score.mode != 1 and (beatmap.passcount / beatmap.playcount) > 0.3:
        base_pp *= 0.2

    score.ppv1 = math.prod([
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

    scores.update(
        score.id,
        {'ppv1': score.ppv1},
        session=session
    )

    return max(0, score.ppv1)

def calculate_weight(pps: List[float]) -> float:
    """Calculate the sum of weighted pp for each score"""
    pps.sort(reverse=True)
    return sum(pp * 0.95**index for index, pp in enumerate(pps))

def calculate_weighted_ppv1(scores: List[DBScore]) -> float:
    """Calculate weighted ppv1 with from a list of scores"""
    return calculate_weight([
        score.ppv1
        for score in scores
    ])

@wrapper.session_wrapper
def recalculate_weighted_ppv1(
    scores: List[DBScore],
    session: Session = ...
) -> float:
    """Calculate weighted ppv1 with from a list of scores"""
    return calculate_weight([
        calculate_ppv1(score, session=session)
        for score in scores
    ])
