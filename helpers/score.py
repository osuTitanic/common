
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
        Mods.Relax: 0.5,
        Mods.Autopilot: 0.5,
    }

    multiplier = functools.reduce(
        (lambda acc, mod: acc * multipliers[mod]),
        (mod for mod in mods.members if mod in multipliers),
        1.00
    )

    return 1.00 * multiplier

def calculate_rx_score(score: DBScore, beatmap: DBBeatmap) -> int:
    """Calculate the total score for relax plays"""
    total_hits = (
        score.n300 +
        score.n100 +
        score.n50 +
        score.nMiss
    )

    if total_hits <= 0:
        return 0

    avg_hit = (
        (300 * (score.n300 / total_hits)) +
        (100 * (score.n100 / total_hits)) +
        (50 * (score.n50 / total_hits))
    )

    mod_multiplier = calculate_mod_multiplier(Mods(score.mods))
    difficulty_multiplier = calculate_difficulty_multiplier(beatmap, total_hits)
    effective_max_combo = score.max_combo
    
    # Fix funny sliderend behaviour
    if not score.nMiss and (beatmap.max_combo-score.max_combo) < 10:
        effective_max_combo = beatmap.max_combo
    
    combo_multipliers = [
        avg_hit * (
            1 + (combo * difficulty_multiplier * mod_multiplier / 25)
        )
        for combo in range(1, effective_max_combo)
    ]
    
    final_score = sum(combo_multipliers)

    return round(final_score)
