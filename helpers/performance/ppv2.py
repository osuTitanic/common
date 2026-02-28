
from app.common.helpers.performance.ppv2_base import PerformanceCalculator, DifficultyAttributes
from app.common.database.objects import DBScore

# Global ppv2 calculator instance, initialized by the application session
calculator: PerformanceCalculator | None = None

def initialize_calculator(instance: PerformanceCalculator) -> None:
    global calculator
    calculator = instance

def calculate_ppv2(score: DBScore) -> float | None:
    assert calculator is not None, "ppv2 calculator has not been initialized"
    return calculator.calculate_ppv2(score)

def calculate_difficulty(beatmap_id: int, mode: int, mods: int) -> DifficultyAttributes | None:
    assert calculator is not None, "ppv2 calculator has not been initialized"
    return calculator.calculate_difficulty(beatmap_id, mode, mods)
