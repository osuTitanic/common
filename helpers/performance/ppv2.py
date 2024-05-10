
from titanic_pp_py import Calculator, Beatmap, DifficultyAttributes

from ...database.objects import DBScore
from ...constants import GameMode, Mods
from typing import Optional

import math
import app

def total_hits(score: DBScore) -> int:
    if score.mode == GameMode.CatchTheBeat:
        return score.n50 + score.n100 + score.n300 + score.nMiss + score.nKatu

    elif score.mode == GameMode.OsuMania:
        return score.n300 + score.n100 + score.n50 + score.nGeki + score.nKatu + score.nMiss

    return score.n50 + score.n100 + score.n300 + score.nMiss

def calculate_ppv2(score: DBScore) -> Optional[float]:
    beatmap_file = app.session.storage.get_beatmap(score.beatmap_id)

    if not beatmap_file:
        app.session.logger.error(
            f'pp calculation failed: Beatmap file was not found! ({score.user_id})'
        )
        return

    mods = Mods(score.mods)

    if Mods.Nightcore in mods and not Mods.DoubleTime in mods:
        # NC somehow only appears with DT enabled at the same time
        # https://github.com/ppy/osu-api/wiki#mods
        mods |= Mods.DoubleTime

    if Mods.Perfect in mods and not Mods.SuddenDeath in mods:
        # The same seems to be the case for PF & SD
        mods |= Mods.SuddenDeath

    if Mods.Hidden in mods and not Mods.FadeIn in mods and score.mode == 3:
        # And also for HD & FI
        mods |= Mods.FadeIn

    if Mods.NoVideo in mods and score.client_version < 20140000:
        # NoVideo was changed to TouchDevice, which affects pp a lot
        mods &= ~Mods.NoVideo

    score.mods = mods.value

    bm = Beatmap(bytes=beatmap_file)

    calc = Calculator(
        mode           = score.mode,
        mods           = score.mods,
        n_geki         = score.nGeki,
        n_katu         = score.nKatu,
        n300           = score.n300,
        n100           = score.n100,
        n50            = score.n50,
        n_misses       = score.nMiss,
        combo          = score.max_combo,
        passed_objects = total_hits(score)
    )

    if not (result := calc.performance(bm)):
        app.session.logger.error(
            'pp calculation failed: No result'
        )
        return

    if math.isnan(result.pp):
        app.session.logger.error(
            'pp calculation failed: NaN pp'
        )
        return 0.0

    if math.isinf(result.pp):
        app.session.logger.error(
            'pp calculation failed: Inf pp'
        )
        return 0.0

    app.session.logger.debug(f"Calculated pp: {result}")

    return result.pp

def calculate_difficulty(beatmap_file: bytes, mode: GameMode, mods: Mods = Mods.NoMod) -> Optional[DifficultyAttributes]:
    bm = Beatmap(bytes=beatmap_file)

    calc = Calculator(
        mode = mode,
        mods = mods.value
    )

    if not (result := calc.difficulty(bm)):
        app.session.logger.error(
            'Difficulty calculation failed: No result'
        )
        return

    if math.isnan(result.stars):
        app.session.logger.error(
            'Difficulty calculation failed: NaN stars'
        )
        return

    if math.isinf(result.stars):
        app.session.logger.error(
            'Difficulty calculation failed: Inf stars'
        )
        return

    app.session.logger.debug(f"Calculated difficulty: {result}")

    return result
