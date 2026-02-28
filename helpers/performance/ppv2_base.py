
from app.common.database.objects import DBScore
from app.common.constants import GameMode, Mods
from app.common.storage import Storage
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from copy import copy

import logging

@dataclass
class DifficultyAttributes:
    mode: GameMode
    mods: Mods
    star_rating: float
    difficulty_attributes: dict[str, Any]
    beatmap_attributes: dict[str, Any]

    @property
    def n_circles(self) -> int:
        return self.beatmap_attributes.get('n_circles', 0)

    @property
    def n_sliders(self) -> int:
        return self.beatmap_attributes.get('n_sliders', 0)

    @property
    def n_spinners(self) -> int:
        return self.beatmap_attributes.get('n_spinners', 0)

    @property
    def max_combo(self) -> int:
        return self.beatmap_attributes.get('max_combo', 0)

class PerformanceCalculator(ABC):
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.logger = logging.getLogger('performance')

    @abstractmethod
    def calculate_ppv2(self, score: DBScore) -> float | None:
        ...

    @abstractmethod
    def calculate_difficulty(self, beatmap_data: bytes, mode: GameMode, mods: Mods) -> DifficultyAttributes | None:
        ...

    def calculate_difficulty_from_id(self, beatmap_id: int, mode: GameMode, mods: Mods) -> DifficultyAttributes | None:
        beatmap_file = self.storage.get_beatmap(beatmap_id)

        if not beatmap_file:
            self.logger.error(f"Difficulty calculation failed: Beatmap file was not found! ({beatmap_id})")
            return

        return self.calculate_difficulty(beatmap_file, mode, mods)

    def calculate_ppv2_if_fc(self, score: DBScore) -> float | None:
        fc_score = copy(score)
        fc_score.max_combo = score.beatmap.max_combo
        fc_score.nMiss = 0
        return self.calculate_ppv2(fc_score)

    @staticmethod
    def adjust_mods(mods: int, mode: int | GameMode, client_version: int = 0) -> Mods:
        mods = Mods(mods)

        if Mods.Nightcore in mods and not Mods.DoubleTime in mods:
            # NC somehow only appears with DT enabled at the same time
            # https://github.com/ppy/osu-api/wiki#mods
            mods |= Mods.DoubleTime
        
        if Mods.Perfect in mods and not Mods.SuddenDeath in mods:
            # The same seems to be the case for PF & SD
            mods |= Mods.SuddenDeath

        if Mods.Hidden in mods and not Mods.FadeIn in mods and mode == GameMode.OsuMania:
            # And also for HD & FI
            mods |= Mods.FadeIn

        if Mods.NoVideo in mods and client_version < 20140000:
            # NoVideo was changed to TouchDevice, which affects pp a lot
            mods &= ~Mods.NoVideo

        return mods
