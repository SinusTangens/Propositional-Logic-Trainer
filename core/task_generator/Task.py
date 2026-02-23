from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Sequence, Dict
from sympy.logic.boolalg import Boolean



class TaskType(Enum):
    DIRECT_INFERENCE = "Direktes Schließen der Variablenbelegungen auf Basis weniger Prämissen"  
    CASE_SPLIT = "Durchführung einer initialen Fallunterscheidung, um alle Variablenbelegungen auf Basis vieler Prämissen zu bestimmen"       


# Anzeigenamen für die TaskTypes (für UI)
TASK_TYPE_DISPLAY_NAMES = {
    TaskType.DIRECT_INFERENCE: "Unit Propagation",
    TaskType.CASE_SPLIT: "Case Split",
}


@dataclass
class Task:
    task_type: TaskType
    level: int
    premises: List[Boolean]   # SymPy-Formeln
    variables: List           # SymPy-Symbole (A, B, C, ...)


@dataclass
class DifficultySpec:
    num_vars_range: Tuple[int, int]
    num_premises_range: Tuple[int, int]
    max_depth: int
    allowed_ops: Sequence[str]  
    op_weights: Dict[str, float]  



# Regelbasierte Konfiguration des Schwierigkeisgrad über die Aufgabentypen und Levels hinweg
DIFFICULTY_CONFIG: Dict[Tuple[TaskType, int], DifficultySpec] = {

    (TaskType.DIRECT_INFERENCE, 1): DifficultySpec(
        num_vars_range=(2, 2),
        num_premises_range=(2, 2),
        max_depth=1,
        allowed_ops=["not", "or", "imp", "xor", "equiv"],
        op_weights={"not": 0.75, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
    ),

    (TaskType.DIRECT_INFERENCE, 2): DifficultySpec(
        num_vars_range=(3, 3),
        num_premises_range=(2, 2),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 0.75, "and": 0.75, "or": 1.0, "imp": 1.0, "xor": 0.5, "equiv": 0.5},
    ),

    (TaskType.DIRECT_INFERENCE, 3): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(2, 2),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 0.75, "and": 0.75, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
    ),

    (TaskType.DIRECT_INFERENCE, 4): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(2, 2),
        max_depth=3,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 0.75, "and": 0.75, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
    ),



    (TaskType.CASE_SPLIT, 1): DifficultySpec(
        num_vars_range=(3, 3), 
        num_premises_range=(4, 4), 
        max_depth=1,
        allowed_ops=["not", "or", "imp", "xor", "equiv"], 
        op_weights={"not": 0.75, "or": 1.0, "imp": 1.0, "xor": 0.75, "equiv": 0.75},
    ),

    (TaskType.CASE_SPLIT, 2): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(5, 5),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 0.75, "or": 1.0, "imp": 1.0, "xor": 0.75, "and": 1.0, "equiv": 0.75},
    ),

    (TaskType.CASE_SPLIT, 3): DifficultySpec(
        num_vars_range=(5, 5),
        num_premises_range=(6, 6),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 0.75, "or": 1.0, "imp": 1.0, "xor": 0.75, "and": 1.0, "equiv": 0.75},
    ),
}


# ============================================================================
# ABGELEITETE KONFIGURATIONEN (automatisch aus DIFFICULTY_CONFIG berechnet)
# ============================================================================

def get_levels_for_task_type(task_type: TaskType) -> List[int]:
    """Gibt alle verfügbaren Levels für einen TaskType zurück."""
    return sorted([level for (tt, level) in DIFFICULTY_CONFIG.keys() if tt == task_type])


def get_max_level(task_type: TaskType) -> int:
    """Gibt das höchste Level für einen TaskType zurück."""
    levels = get_levels_for_task_type(task_type)
    return max(levels) if levels else 1


def get_all_task_types() -> List[TaskType]:
    """Gibt alle TaskTypes zurück, die in DIFFICULTY_CONFIG definiert sind."""
    return list(set(tt for (tt, _) in DIFFICULTY_CONFIG.keys()))


def get_total_levels() -> int:
    """Gibt die Gesamtanzahl aller Levels über alle TaskTypes zurück."""
    return sum(get_max_level(tt) for tt in get_all_task_types())
