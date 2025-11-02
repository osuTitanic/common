
from __future__ import annotations

from app.common.database.repositories import scores, beatmaps, wrapper
from app.common.database.objects import DBScore, DBBeatmap
from app.common.constants import Mods, GameMode

from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

import math

# ppv1 reference: https://gist.github.com/peppy/4f8fcb6629d300c56ebe80156b20b76c

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

    star_rating = resolve_star_rating(beatmap, session)
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

@wrapper.session_wrapper
def resolve_star_rating(beatmap: DBBeatmap, session: Session = ...) -> float:
    # NOTE: We're using ppv2-based star ratings for now, until the
    #       old eyup star rating implementation matches the original
    return min(5, beatmap.diff * 0.565)

    if beatmap.diff_eyup:
        return beatmap.diff_eyup

    beatmap.diff_eyup = calculate_star_rating(beatmap)
    beatmaps.update(beatmap.id, {'diff_eyup': beatmap.diff_eyup}, session)
    return beatmap.diff_eyup

def calculate_star_rating(beatmap: DBBeatmap) -> float:
    """Calculate the old eyup star rating"""
    if beatmap.drain_length <= 0:
        return 0

    if beatmap.mode == GameMode.OsuMania:
        notes = (
            beatmap.count_normal + beatmap.count_slider * 1.2
        )
        return (
            (beatmap.hp / 14 + beatmap.od / 12) +
            (notes / beatmap.drain_length) / 2.3 * math.pow(1.04, beatmap.cs - 3)
        )

    total_objects = (
        beatmap.count_normal +
        beatmap.count_slider*2 +
        beatmap.count_spinner*3
    )

    noteDensity = total_objects / beatmap.drain_length
    difficulty = beatmap.hp + beatmap.od + beatmap.cs

    if beatmap.count_slider / total_objects >= 0.1:
        bpm = (beatmap.bpm / 60) * beatmap.slider_multiplier
        difficulty = (difficulty + max(0, min(4, (bpm - 1.5) * 2.5))) * 0.75

    # Songs with insane accuracy/circle size/life drain
    if difficulty > 21:
        return (min(difficulty, 30) / 3 * 4 + min(20 - 0.032 * math.pow(noteDensity - 5, 4), 20)) / 10
    
    # Songs with insane number of beats per second
    if noteDensity >= 2.5:
        return (min(difficulty, 18) / 18 * 10 + min(40 - 40 / math.pow(5, 3.5) * math.pow(min(noteDensity, 5) - 5, 4), 40)) / 10
    
    # Songs with glacial number of beats per second
    if noteDensity < 1:
        return (min(difficulty, 18) / 18 * 10) / 10 + 0.25

    # All other songs of medium difficulty
    return (min(difficulty, 18) / 18 * 10 + min(25 * (noteDensity - 1), 40)) / 10
