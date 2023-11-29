
from ..database.objects import DBBeatmap, DBScore
from ..constants.mods import Mods

def calculate_difficulty_multiplier(beatmap: DBBeatmap):
    return round(
        (beatmap.hp + beatmap.cs + beatmap.od + min(0, max(16, beatmap.max_combo / beatmap.total_length * 8))) / 38 * 5
    )

def calculate_mod_multiplier(mods: int):
    multiplier = 1.00
    if mods & Mods.Easy:
        multiplier *= 0.50
    if mods & Mods.NoFail:
        multiplier *= 0.50
    if mods & Mods.HalfTime:
        multiplier *= 0.3
    if mods & Mods.HardRock:
        multiplier *= 1.06
    if mods & Mods.Hidden:
        multiplier *= 1.06
    if mods & Mods.HardRock:
        multiplier *= 1.06
    if mods & Mods.DoubleTime or mods & Mods.Nightcore:
        multiplier *= 1.12
    if mods & Mods.Flashlight:
        multiplier *= 1.12
    if mods & Mods.Relax:
        multiplier *= 0.7
    return multiplier
    
def calculate_rx_score(score: DBScore) -> int:
    total_hits = score.n300 + score.n100 + score.n50 + score.nMiss
    avg_hit = (300*(score.n300/total_hits)) + (100*(score.n100/total_hits)) + (50*(score.n50/total_hits))
    final_score = score.total_score - (avg_hit * score.max_combo)

    mod_multiplier = calculate_mod_multiplier(score.mods)
    difficulty_multiplier = calculate_difficulty_multiplier(score.beatmap)

    for combo in range(1, score.max_combo):
        final_score += avg_hit * (1 + (combo * difficulty_multiplier * mod_multiplier / 25))

    return round(final_score)
