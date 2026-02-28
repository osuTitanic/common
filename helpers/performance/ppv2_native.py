
from app.common.helpers import score as score_helper
from app.common.constants.mods import ModMapping
from app.common.database.objects import DBScore
from app.common.constants import GameMode, Mods
from math import isinf, isnan
from typing import Any

from osu_native_py.wrapper.calculators import (
    create_difficulty_calculator,
    create_performance_calculator,
)
from osu_native_py.wrapper.attributes import (
    DifficultyAttributes as NativeDifficultyAttributes,
    OsuDifficultyAttributes as NativeOsuDifficultyAttributes,
    TaikoDifficultyAttributes as NativeTaikoDifficultyAttributes,
    CatchDifficultyAttributes as NativeCatchDifficultyAttributes,
    ManiaDifficultyAttributes as NativeManiaDifficultyAttributes,
)
from osu_native_py.wrapper.objects import (
    Beatmap as NativeBeatmap,
    Mod as NativeMod,
    ModsCollection,
    Ruleset,
    ScoreInfo,
)

from .ppv2 import DifficultyAttributes, PerformanceCalculator

class NativePerformanceCalculator(PerformanceCalculator):
    def calculate_ppv2(self, score: DBScore) -> float | None:
        beatmap_file = self.storage.get_beatmap(score.beatmap_id)

        if not beatmap_file:
            self.logger.error(
                f"pp calculation failed: Beatmap file was not found! ({score.beatmap_id})"
            )
            return

        mods = self.adjust_mods(
            score.mods,
            score.mode,
            score.client_version
        )

        if Mods.Relax in mods or Mods.Autopilot in mods:
            return 0.0

        ruleset = self.convert_to_native_ruleset(score.mode)
        native_mods = self.convert_to_native_mods(mods)
        native_beatmap = self.load_native_beatmap(beatmap_file)

        if not native_beatmap:
            self.logger.error(
                f"pp calculation failed: Beatmap file could not be parsed! ({score.beatmap_id})"
            )
            return

        try:
            diff_calculator = create_difficulty_calculator(ruleset, native_beatmap)
            perf_calculator = create_performance_calculator(ruleset)
            diff_attributes = diff_calculator.calculate(native_mods)

            result = perf_calculator.calculate(
                ruleset,
                native_beatmap,
                native_mods,
                self.convert_to_score_info(score),
                diff_attributes,
            )

            if not result:
                self.logger.error("pp calculation failed: No result")
                return

            if isnan(result.total):
                self.logger.error("pp calculation failed: NaN pp")
                return 0.0

            if isinf(result.total):
                self.logger.error("pp calculation failed: Inf pp")
                return 0.0

            self.logger.debug(f"Calculated pp: {result}")
            return float(result.total)
        except Exception as exc:
            self.logger.error(f"pp calculation failed: {exc}")
        finally:
            self.close_native_objects(native_beatmap, ruleset)

    def calculate_difficulty(
        self,
        beatmap_file: bytes,
        mode: GameMode,
        mods: Mods,
    ) -> DifficultyAttributes | None:
        adjusted_mods = self.adjust_mods(mods, mode)
        ruleset = self.convert_to_native_ruleset(mode)
        native_mods = self.convert_to_native_mods(adjusted_mods)
        native_beatmap = self.load_native_beatmap(beatmap_file)

        if not native_beatmap:
            self.logger.error(
                f"Difficulty calculation failed: Beatmap file could not be parsed!"
            )
            return

        try:
            calculator = create_difficulty_calculator(ruleset, native_beatmap)
            result = calculator.calculate(native_mods)

            if not result:
                self.logger.error("Difficulty calculation failed: No result")
                return

            if isnan(result.star_rating):
                self.logger.error("Difficulty calculation failed: NaN stars")
                return

            if isinf(result.star_rating):
                self.logger.error("Difficulty calculation failed: Inf stars")
                return

            self.logger.debug(f"Calculated difficulty: {result}")
            return self.map_difficulty_attributes(
                result=result,
                mode=self.convert_to_game_mode(ruleset.ruleset_id),
                mods=adjusted_mods,
                beatmap=native_beatmap,
            )
        except Exception as exc:
            self.logger.error(f"Difficulty calculation failed: {exc}")
        finally:
            self.close_native_objects(native_beatmap, ruleset)

    @staticmethod
    def map_difficulty_attributes(
        result: NativeDifficultyAttributes,
        mode: GameMode,
        mods: Mods,
        beatmap: NativeBeatmap,
    ) -> DifficultyAttributes:
        difficulty_attributes: dict[str, Any] = {
            "aim": getattr(result, "aim_difficulty", None),
            "aim_difficult_slider_count": getattr(result, "aim_difficult_slider_count", None),
            "speed": getattr(result, "speed_difficulty", None),
            "flashlight": getattr(result, "flashlight_difficulty", None),
            "slider_factor": getattr(result, "slider_factor", None),
            "speed_note_count": getattr(result, "speed_note_count", None),
            "aim_difficult_strain_count": getattr(result, "aim_difficult_strain_count", None),
            "speed_difficult_strain_count": getattr(result, "speed_difficult_strain_count", None),
            "stamina": getattr(result, "stamina_difficulty", None),
            "reading": getattr(result, "reading_difficulty", None),
            "rhythm": getattr(result, "rhythm_difficulty", None),
            "color": getattr(result, "colour_difficulty", None),
        }
        beatmap_attributes: dict[str, Any] = {
            "hp": getattr(beatmap, "drain_rate", None),
            "ar": getattr(beatmap, "approach_rate", None),
            "n_circles": getattr(result, "hit_circle_count", None),
            "n_sliders": getattr(result, "slider_count", None),
            "n_spinners": getattr(result, "spinner_count", None),
            "n_objects": sum(
                value for value in (
                    getattr(result, "hit_circle_count", 0),
                    getattr(result, "slider_count", 0),
                    getattr(result, "spinner_count", 0)
                )
            ),
            "max_combo": getattr(result, "max_combo", None),
        }

        return DifficultyAttributes(
            mode=mode,
            mods=mods,
            star_rating=float(result.star_rating),
            difficulty_attributes=difficulty_attributes,
            beatmap_attributes=beatmap_attributes
        )

    @staticmethod
    def convert_to_native_ruleset(mode: GameMode | int | Ruleset) -> Ruleset:
        if isinstance(mode, Ruleset):
            return mode

        return Ruleset.from_id(int(mode))

    @staticmethod
    def convert_to_game_mode(mode: int | GameMode | Ruleset) -> GameMode:
        if isinstance(mode, GameMode):
            return mode

        if isinstance(mode, Ruleset):
            mode = mode.ruleset_id

        mapping = {
            0: GameMode.Osu,
            1: GameMode.Taiko,
            2: GameMode.CatchTheBeat,
            3: GameMode.OsuMania,
        }
        return mapping.get(int(mode), GameMode.Osu)

    @staticmethod
    def convert_to_native_mods(mods: Mods) -> ModsCollection:
        collection = ModsCollection.create()

        for mod in mods.members:
            short_name = ModMapping.get(mod)
            if not short_name or short_name == "NM":
                continue

            collection.add(NativeMod.create(short_name))

        return collection

    @staticmethod
    def convert_to_score_info(score: DBScore) -> ScoreInfo:
        return ScoreInfo(
            accuracy=score.acc or score_helper.calculate_accuracy(score),
            legacy_total_score=score.total_score,
            max_combo=score.max_combo,
            count_great=score.n300,
            count_ok=score.n100,
            count_meh=score.n50,
            count_miss=score.nMiss,
            count_perfect=score.nGeki,
            count_good=score.nKatu
        )

    @staticmethod
    def load_native_beatmap(beatmap_file: bytes) -> NativeBeatmap | None:
        try:
            beatmap_text = beatmap_file.decode("utf-8-sig", errors="replace")
            return NativeBeatmap.from_text(beatmap_text)
        except Exception:
            return None

    @staticmethod
    def close_native_objects(beatmap: NativeBeatmap | None, ruleset: Ruleset | None) -> None:
        if beatmap and not beatmap.is_closed:
            beatmap.close()

        if ruleset and not ruleset.is_closed:
            ruleset.close()
