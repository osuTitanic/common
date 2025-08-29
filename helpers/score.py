
from ..database.objects import DBBeatmap, DBScore
from ..constants.mods import Mods

import functools

def calculate_difficulty_multiplier(beatmap: DBBeatmap, total_hits: int):
    """Get the beatmap difficulty multiplier for score calculations"""
    return round(
        (
            beatmap.hp +
            beatmap.cs +
            beatmap.od +
            min(0, max(16, total_hits / beatmap.total_length * 8))
        ) / 38 * 5
    )

def calculate_mod_multiplier(mods: Mods) -> float:
    """Get the mod multiplier for score calculations"""
    multipliers = {
        Mods.Easy: 0.50,
        Mods.NoFail: 0.50,
        Mods.HalfTime: 0.3,
        Mods.HardRock: 1.06,
        Mods.Hidden: 1.06,
        Mods.DoubleTime: 1.12,
        Mods.Nightcore: 1.12,
        Mods.Flashlight: 1.12,
        Mods.Relax: 0.3,
        Mods.Autopilot: 0.3,
    }

    multiplier = functools.reduce(
        (lambda acc, mod: acc * multipliers[mod]),
        (mod for mod in mods.members if mod in multipliers),
        1.00
    )

    return 1.00 * multiplier

def calculate_rx_score(score: DBScore, beatmap: DBBeatmap) -> int:
    """Calculate the total score for relax plays"""
    if score.mode == 2:
        return score.total_score * 0.25

    if score.mode != 0:
        return score.total_score

    total_hits = (
        score.n300 +
        score.n100 +
        score.n50 +
        score.nMiss
    )
    
    original_score = (
        (score.n300 * 300) +
        (score.n100 * 100) +
        (score.n50 * 50)
    )

    if total_hits <= 0:
        return 0

    # Account for slider ticks inflating score
    slider_factor = beatmap.max_combo / total_hits

    avg_hit = (
        (300 * (score.n300 / total_hits)) +
        (100 * (score.n100 / total_hits)) +
        (50 * (score.n50 / total_hits))
    ) / slider_factor

    mod_multiplier = calculate_mod_multiplier(Mods(score.mods))
    difficulty_multiplier = calculate_difficulty_multiplier(beatmap, total_hits)

    combo_multipliers = [
        avg_hit * (
            1 + (combo * difficulty_multiplier * mod_multiplier / 25)
        )
        for combo in range(1, score.max_combo)
    ]

    final_score = original_score + sum(combo_multipliers)

    return round(final_score)
