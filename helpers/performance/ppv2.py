
from __future__ import annotations
from rosu_pp_py import (
    DifficultyAttributes,
    Performance,
    GameMode,
    Beatmap
)

from app.common.database.objects import DBScore
from app.common.constants import Mods
from copy import copy

import math
import app

def calculate_ppv2(score: DBScore) -> float | None:
    beatmap_file = app.session.storage.get_beatmap(score.beatmap_id)

    if not beatmap_file:
        app.session.logger.error(
            f'pp calculation failed: Beatmap file was not found! ({score.beatmap_id})'
        )
        return


    # Some older clients need adjustments to mods
    mods = adjust_mods(score)
    mode = convert_mode(score.mode)

    # Load beatmap file & convert it
    beatmap = Beatmap(bytes=beatmap_file)
    beatmap.convert(mode, mods.value)

    if beatmap.is_suspicious():
        app.session.logger.error(
            f'pp calculation failed: Beatmap file is suspicious! ({score.beatmap_id})'
        )
        return

    perf = Performance(
        lazer=False,
        mods=mods.value,
        n_geki=score.nGeki,
        n_katu=score.nKatu,
        n300=score.n300,
        n100=score.n100,
        n50=score.n50,
        misses=score.nMiss,
        combo=score.max_combo,
        passed_objects=total_hits(score),
    )

    relaxing = Mods.Relax in mods or Mods.Autopilot in mods
    mode_multiplier = 0.15 if mode != GameMode.Osu and relaxing else 1.0

    if not (result := perf.calculate(beatmap)):
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
    return result.pp * mode_multiplier

def calculate_ppv2_if_fc(score: DBScore) -> float | None:
    fc_score = copy(score)
    fc_score.max_combo = score.beatmap.max_combo
    fc_score.nMiss = 0
    return calculate_ppv2(fc_score)

def calculate_difficulty(
    beatmap_file: bytes,
    mode: GameMode | int = GameMode.Osu,
    mods: Mods = Mods.NoMod
) -> DifficultyAttributes | None:
    if isinstance(mode, int):
        mode = convert_mode(mode)
        
    if not beatmap_file:
        app.session.logger.error(
            'Difficulty calculation failed: Beatmap file was not found!'
        )
        return

    perf = Performance(mods=mods.value)
    beatmap = Beatmap(bytes=beatmap_file)
    beatmap.convert(mode, mods.value)
    difficulty = perf.difficulty()

    if not (result := difficulty.calculate(beatmap)):
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

def adjust_mods(score: DBScore) -> Mods:
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

    return mods

def total_hits(score: DBScore) -> int:
    if score.mode == GameMode.Catch:
        return score.n50 + score.n100 + score.n300 + score.nMiss + score.nKatu

    elif score.mode == GameMode.Mania:
        return score.n300 + score.n100 + score.n50 + score.nGeki + score.nKatu + score.nMiss

    return score.n50 + score.n100 + score.n300 + score.nMiss

def convert_mode(mode: int) -> GameMode:
    mapping = {
        0: GameMode.Osu,
        1: GameMode.Taiko,
        2: GameMode.Catch,
        3: GameMode.Mania
    }
    return mapping.get(mode, GameMode.Osu)
