
from dataclasses import dataclass
from functools import reduce
from operator import mul

from ...constants import Mods

from datetime import datetime
from typing import List

import math

__all__ = (
    'calculate_weighted_ppv1',
    'calculate_ppv1',
    'Score',
    'Mods'
)

@dataclass
class Score:
    rank: int
    acc: float
    mods: Mods
    full_combo: bool
    submission_time: datetime
    beatmap_difficulty: float
    beatmap_playcount: int

factors = {
    Mods.HardRock: 1.25,
    Mods.Nightcore: 1.35,
    Mods.DoubleTime: 1.2,
    Mods.Flashlight: 1.15,
    Mods.Hidden: 1.05,
    Mods.NoFail: 0.95,
    Mods.SpunOut: 0.90,
    Mods.Autopilot: 0.5,
    Mods.Relax: 0.5,
    Mods.HalfTime: 0.25,
    Mods.Easy: 0.3,
    Mods.Autoplay: 0.0
}

def calculate_weight(pps: List[float]) -> float:
    pps.sort(reverse=True)
    return sum(pp * 0.95**index for index, pp in enumerate(pps))

def calculate_ppv1(
    score: Score,
    age_falloff: int = 365,
    rank_falloff: int = 500,
    populariy_falloff: int = 100000,
    difficulty_multiplier: int = 45
) -> float:
    score_age = (datetime.now() - score.submission_time).days
    populariy_factor = math.log(score.beatmap_playcount, populariy_falloff)

    # Multiply based on beatmap star rating
    score.beatmap_difficulty *= difficulty_multiplier

    age_factor = (
        math.log(-1 * score_age + (age_falloff + 1), age_falloff + 1) + 0.01
        if score_age <= age_falloff else 0.01
    )

    rank_factor = (
        min(1, (-1 * math.log(score.rank, rank_falloff) + 1) + 0.01)
        if score.rank <= rank_falloff else 0.01
    )

    mod_factors = [
        factor for mod, factor in factors.items()
        if mod in score.mods
    ]

    mods_factor = (
        reduce(mul, mod_factors)
        if mod_factors else 1
    )

    acc_bonus = 1.2 if score.acc == 1 else 1
    fc_bonus = 1.15 if score.full_combo and score.acc < 1 else 1

    return (score.beatmap_difficulty * score.acc * populariy_factor * age_factor * rank_factor * mods_factor * acc_bonus * fc_bonus)

def calculate_weighted_ppv1(
    scores: List[Score],
    age_falloff: int = 365,
    rank_falloff: int = 500,
    populariy_falloff: int = 100000,
    difficulty_multiplier: int = 45
) -> float:
    return calculate_weight([
        calculate_ppv1(
            score,
            age_falloff,
            rank_falloff,
            populariy_falloff,
            difficulty_multiplier
        )
        for score in scores
    ])
