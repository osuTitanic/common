
from ...database.repositories import scores
from ...database.objects import DBScore

from datetime import datetime
from typing import List

import math

def calculate_weight(pps: List[float]) -> float:
    """Calculate the sum of weighted pp for each score"""
    pps.sort(reverse=True)
    return sum(pp * 0.95**index for index, pp in enumerate(pps))

def calculate_ppv1(
    score: DBScore,
    age_falloff: int = 365,
    rank_falloff: int = 500,
    populariy_falloff: int = 1000
) -> float:
    """Calculate ppv1, by using the score's pp as a difficulty factor"""
    if score.beatmap.playcount <= 0:
        return 0

    score_age = (datetime.now() - score.submitted_at.replace(tzinfo=None)).days
    populariy_factor = math.log(score.beatmap.playcount, populariy_falloff)

    age_factor = (
        math.log(-1 * score_age + (age_falloff + 1), age_falloff + 1) + 0.01
        if score_age <= age_falloff else 0.01
    )

    score_rank = scores.fetch_score_index_by_tscore(
        score.total_score,
        score.beatmap.id,
        score.mode
    )

    rank_factor = (
        min(1, (-1 * math.log(score_rank, rank_falloff) + 1) + 0.01)
        if score_rank <= rank_falloff else 0.01
    )

    acc_bonus = 1.2 if score.acc == 1 else 1
    fc_bonus = 1.15 if score.perfect and score.acc < 1 else 1

    return (score.pp * score.acc * populariy_factor * age_factor * rank_factor * acc_bonus * fc_bonus)

def calculate_weighted_ppv1(
    scores: List[DBScore],
    age_falloff: int = 365,
    rank_falloff: int = 500,
    populariy_falloff: int = 1000
) -> float:
    """Calculate weighted ppv1 with from a list of scores"""
    return calculate_weight([
        calculate_ppv1(
            score,
            age_falloff,
            rank_falloff,
            populariy_falloff
        )
        for score in scores
    ])
