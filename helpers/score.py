
from ..database.objects import DBBeatmap, DBScore
from ..constants.mods import Mods

def calculate_difficulty_multiplier(beatmap: DBBeatmap, total_hits: int):
    """Get the beatmap difficulty multiplier for score calculations"""
    return round(
        (beatmap.hp + beatmap.cs + beatmap.od + min(0, max(16, total_hits / beatmap.total_length * 8))) / 38 * 5
    )

def calculate_mod_multiplier(mods: Mods) -> float:
    """Get the mod multiplier for score calculations"""
    multiplier = 1.00
    if Mods.Easy in mods:
        multiplier *= 0.50
    if Mods.NoFail in mods:
        multiplier *= 0.50
    if Mods.HalfTime in mods:
        multiplier *= 0.3
    if Mods.HardRock in mods:
        multiplier *= 1.06
    if Mods.Hidden in mods:
        multiplier *= 1.06
    if Mods.HardRock in mods:
        multiplier *= 1.06
    if Mods.DoubleTime in mods or Mods.Nightcore in mods:
        multiplier *= 1.12
    if Mods.Flashlight in mods:
        multiplier *= 1.12
    if Mods.Relax in mods:
        multiplier *= 0.7
    return multiplier
    
def calculate_rx_score(score: DBScore) -> int:
    """Recalculate the total score for relax plays"""
    total_hits = score.n300 + score.n100 + score.n50 + score.nMiss
    avg_hit = (300*(score.n300/total_hits)) + (100*(score.n100/total_hits)) + (50*(score.n50/total_hits))
    final_score = score.total_score - (avg_hit * score.max_combo)

    mod_multiplier = calculate_mod_multiplier(Mods(score.mods))
    difficulty_multiplier = calculate_difficulty_multiplier(score.beatmap, total_hits)

    for combo in range(1, score.max_combo):
        final_score += avg_hit * (1 + (combo * difficulty_multiplier * mod_multiplier / 25))

    return round(final_score)
