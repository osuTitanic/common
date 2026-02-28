
from app.common.helpers import score as score_helper
from app.common.database.objects import DBScore
from app.common.constants import Mods, GameMode
from math import isnan, isinf

from .ppv2 import (
    PerformanceCalculator,
    DifficultyAttributes
)

from rosu_pp_py import (
    DifficultyAttributes as RosuDifficultyAttributes,
    Performance as RosuPerformance,
    GameMode as RosuGameMode,
    Beatmap as RosuBeatmap
)

class RosuPerformanceCalculator(PerformanceCalculator):
    def calculate_ppv2(self, score: DBScore) -> float | None:
        beatmap_file = self.storage.get_beatmap(score.beatmap_id)

        if not beatmap_file:
            self.logger.error(
                f'pp calculation failed: Beatmap file was not found! ({score.beatmap_id})'
            )
            return

        mods = self.adjust_mods(score.mods, score.mode, score.client_version)
        mode = self.convert_to_rosu_mode(score.mode)

        total_hits = score_helper.calculate_total_hits(score)
        relaxing = Mods.Relax in mods or Mods.Autopilot in mods

        if relaxing:
            return 0.0

        # Load beatmap file & convert it
        beatmap = RosuBeatmap(bytes=beatmap_file)
        beatmap.convert(mode, mods.value)

        if beatmap.is_suspicious():
            self.logger.error(
                f'pp calculation failed: Beatmap file is suspicious! ({score.beatmap_id})'
            )
            return

        perf = RosuPerformance(
            lazer=False,
            mods=mods.value,
            n_geki=score.nGeki,
            n_katu=score.nKatu,
            n300=score.n300,
            n100=score.n100,
            n50=score.n50,
            misses=score.nMiss,
            combo=score.max_combo,
            passed_objects=total_hits
        )

        if not (result := perf.calculate(beatmap)):
            self.logger.error(
                'pp calculation failed: No result'
            )
            return

        if isnan(result.pp):
            self.logger.error(
                'pp calculation failed: NaN pp'
            )
            return 0.0

        if isinf(result.pp):
            self.logger.error(
                'pp calculation failed: Inf pp'
            )
            return 0.0

        self.logger.debug(f"Calculated pp: {result}")
        return result.pp

    def calculate_difficulty(
        self,
        beatmap_file: bytes,
        mode: GameMode,
        mods: int
    ) -> DifficultyAttributes | None:
        adjusted_mods = self.adjust_mods(mods, mode)
        result = self.calculate_rosu_difficulty(beatmap_file, mode, adjusted_mods)

        if not result:
            return

        self.logger.debug(f"Calculated difficulty: {result}")
        return self.map_difficulty_attributes(result, adjusted_mods)

    def calculate_rosu_difficulty(
        self,
        beatmap_file: bytes,
        mode: GameMode | int,
        mods: Mods
    ) -> RosuDifficultyAttributes | None:
        converted_mode = RosuPerformanceCalculator.convert_to_rosu_mode(mode)
        perf = RosuPerformance(mods=mods.value)
        beatmap = RosuBeatmap(bytes=beatmap_file)
        beatmap.convert(converted_mode, mods.value)
        difficulty = perf.difficulty()

        if not (result := difficulty.calculate(beatmap)):
            self.logger.error(
                'Difficulty calculation failed: No result'
            )
            return

        if isnan(result.stars):
            self.logger.error(
                'Difficulty calculation failed: NaN stars'
            )
            return

        if isinf(result.stars):
            self.logger.error(
                'Difficulty calculation failed: Inf stars'
            )
            return

        return result

    @staticmethod
    def map_difficulty_attributes(result: RosuDifficultyAttributes, mods: Mods) -> DifficultyAttributes:
        difficulty_attributes = {
            'aim': result.aim,
            'aim_difficult_slider_count': result.aim_difficult_slider_count,
            'speed': result.speed,
            'flashlight': result.flashlight,
            'slider_factor': result.slider_factor,
            'speed_note_count': result.speed_note_count,
            'aim_difficult_strain_count': result.aim_difficult_strain_count,
            'speed_difficult_strain_count': result.speed_difficult_strain_count,
            'stamina': result.stamina,
            'reading': result.reading,
            'rhythm': result.rhythm,
            'color': result.color
        }
        return DifficultyAttributes(
            mode=RosuPerformanceCalculator.convert_to_game_mode(result.mode),
            mods=mods,
            star_rating=result.stars,
            max_combo=result.max_combo,
            difficulty_attributes={
                key: value for key, value in difficulty_attributes.items()
                if value is not None
            }
        )

    @staticmethod
    def convert_to_rosu_mode(mode: GameMode | int | RosuGameMode) -> RosuGameMode:
        if isinstance(mode, RosuGameMode):
            return mode

        mapping = {
            int(GameMode.Osu): RosuGameMode.Osu,
            int(GameMode.Taiko): RosuGameMode.Taiko,
            int(GameMode.CatchTheBeat): RosuGameMode.Catch,
            int(GameMode.OsuMania): RosuGameMode.Mania
        }
        return mapping.get(int(mode), RosuGameMode.Osu)

    @staticmethod
    def convert_to_game_mode(mode: RosuGameMode | int | GameMode) -> GameMode:
        if isinstance(mode, GameMode):
            return mode

        mapping = {
            int(RosuGameMode.Osu): GameMode.Osu,
            int(RosuGameMode.Taiko): GameMode.Taiko,
            int(RosuGameMode.Catch): GameMode.CatchTheBeat,
            int(RosuGameMode.Mania): GameMode.OsuMania
        }
        return mapping.get(int(mode), GameMode.Osu)
