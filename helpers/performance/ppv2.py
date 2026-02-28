
from app.common.helpers.performance.ppv2_base import PerformanceCalculator, DifficultyAttributes
from app.common.database.objects import DBScore
from app.common.constants import GameMode, Mods

# Global ppv2 calculator instance, initialized by the application session
calculator: PerformanceCalculator | None = None

def initialize_calculator(instance: PerformanceCalculator) -> None:
    global calculator
    calculator = instance

def calculate_ppv2(score: DBScore) -> float | None:
    assert calculator is not None, "ppv2 calculator has not been initialized"
    return calculator.calculate_ppv2(score)

def calculate_difficulty(beatmap_file: bytes, mode: GameMode, mods: Mods = Mods.NoMod) -> DifficultyAttributes | None:
    assert calculator is not None, "ppv2 calculator has not been initialized"
    return calculator.calculate_difficulty(beatmap_file, mode, mods)
