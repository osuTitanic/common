
from app.common.database.objects import DBScore

from .ppv2_base import PerformanceCalculator, DifficultyAttributes
from .ppv2_rosu import RosuPerformanceCalculator

# Global ppv2 calculator instance, initialized by the application session
calculator: PerformanceCalculator

def initialize_calculator(instance: PerformanceCalculator) -> None:
    global calculator
    calculator = instance

def calculate_ppv2(score: DBScore) -> float | None:
    return calculator.calculate_ppv2(score)

def calculate_difficulty(beatmap_id: int, mode: int, mods: int) -> DifficultyAttributes | None:
    return calculator.calculate_difficulty(beatmap_id, mode, mods)
